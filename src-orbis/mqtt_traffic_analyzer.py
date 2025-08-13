#!/usr/bin/env python3
"""
MQTT Traffic Analyzer für Fischertechnik APS
Orbis Development - Traffic Analysis und Reporting
"""

import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class MQTTTrafficAnalyzer:
    """Analyzer für MQTT Traffic Daten"""
    
    def __init__(self, db_file: str = "mqtt_traffic.db"):
        self.db_file = db_file
        self.db_conn = sqlite3.connect(db_file)
        self.db_cursor = self.db_conn.cursor()
    
    def get_message_count(self, hours: int = 24) -> Dict[str, int]:
        """Get message count for the last N hours"""
        since = datetime.now() - timedelta(hours=hours)
        since_str = since.isoformat()
        
        self.db_cursor.execute('''
            SELECT direction, COUNT(*) 
            FROM mqtt_messages 
            WHERE timestamp >= ?
            GROUP BY direction
        ''', (since_str,))
        
        results = dict(self.db_cursor.fetchall())
        return {
            "cloud_to_local": results.get("cloud_to_local", 0),
            "local_to_cloud": results.get("local_to_cloud", 0),
            "total": sum(results.values())
        }
    
    def get_top_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top topics by message count"""
        self.db_cursor.execute('''
            SELECT topic, COUNT(*) as count, 
                   COUNT(CASE WHEN direction = 'cloud_to_local' THEN 1 END) as cloud_to_local,
                   COUNT(CASE WHEN direction = 'local_to_cloud' THEN 1 END) as local_to_cloud
            FROM mqtt_messages 
            GROUP BY topic 
            ORDER BY count DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in self.db_cursor.fetchall():
            results.append({
                "topic": row[0],
                "total_count": row[1],
                "cloud_to_local": row[2],
                "local_to_cloud": row[3]
            })
        
        return results
    
    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent messages"""
        self.db_cursor.execute('''
            SELECT timestamp, direction, topic, payload, qos, retained
            FROM mqtt_messages 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in self.db_cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "direction": row[1],
                "topic": row[2],
                "payload": row[3],
                "qos": row[4],
                "retained": bool(row[5])
            })
        
        return results
    
    def get_module_activity(self) -> Dict[str, Dict[str, int]]:
        """Get activity per module"""
        self.db_cursor.execute('''
            SELECT topic, direction, COUNT(*) as count
            FROM mqtt_messages 
            WHERE topic LIKE 'module/v1/ff/%'
            GROUP BY topic, direction
        ''')
        
        module_activity = {}
        for row in self.db_cursor.fetchall():
            topic, direction, count = row
            
            # Extract module serial number
            parts = topic.split('/')
            if len(parts) >= 4:
                module = parts[3]
                
                if module not in module_activity:
                    module_activity[module] = {"cloud_to_local": 0, "local_to_cloud": 0}
                
                module_activity[module][direction] = count
        
        return module_activity
    
    def get_message_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get message timeline for the last N hours"""
        since = datetime.now() - timedelta(hours=hours)
        since_str = since.isoformat()
        
        self.db_cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                direction,
                COUNT(*) as count
            FROM mqtt_messages 
            WHERE timestamp >= ?
            GROUP BY hour, direction
            ORDER BY hour
        ''', (since_str,))
        
        results = []
        for row in self.db_cursor.fetchall():
            results.append({
                "hour": row[0],
                "direction": row[1],
                "count": row[2]
            })
        
        return results
    
    def export_to_csv(self, filename: str = "mqtt_traffic_export.csv"):
        """Export all messages to CSV"""
        query = '''
            SELECT timestamp, direction, topic, payload, qos, retained
            FROM mqtt_messages 
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, self.db_conn)
        df.to_csv(filename, index=False)
        print(f"📊 Exported {len(df)} messages to {filename}")
    
    def create_visualizations(self, output_dir: str = "traffic_analysis"):
        """Create visualization charts"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Message count by direction
        counts = self.get_message_count()
        
        plt.figure(figsize=(10, 6))
        directions = list(counts.keys())[:-1]  # Exclude total
        values = [counts[d] for d in directions]
        
        plt.bar(directions, values, color=['#ff7f0e', '#2ca02c'])
        plt.title('MQTT Messages by Direction')
        plt.ylabel('Message Count')
        plt.savefig(f"{output_dir}/message_direction.png")
        plt.close()
        
        # 2. Top topics
        top_topics = self.get_top_topics(10)
        
        plt.figure(figsize=(12, 8))
        topics = [t['topic'] for t in top_topics]
        counts = [t['total_count'] for t in top_topics]
        
        plt.barh(topics, counts)
        plt.title('Top MQTT Topics')
        plt.xlabel('Message Count')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_topics.png")
        plt.close()
        
        # 3. Module activity
        module_activity = self.get_module_activity()
        
        if module_activity:
            plt.figure(figsize=(12, 6))
            modules = list(module_activity.keys())
            cloud_to_local = [module_activity[m]['cloud_to_local'] for m in modules]
            local_to_cloud = [module_activity[m]['local_to_cloud'] for m in modules]
            
            x = range(len(modules))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], cloud_to_local, width, label='Cloud → Local', color='#ff7f0e')
            plt.bar([i + width/2 for i in x], local_to_cloud, width, label='Local → Cloud', color='#2ca02c')
            
            plt.xlabel('Modules')
            plt.ylabel('Message Count')
            plt.title('Module Activity')
            plt.xticks(x, modules)
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{output_dir}/module_activity.png")
            plt.close()
        
        print(f"📊 Visualizations saved to {output_dir}/")
    
    def print_summary(self):
        """Print traffic summary"""
        print("\n" + "="*80)
        print("📊 MQTT TRAFFIC ANALYSIS SUMMARY")
        print("="*80)
        
        # Message counts
        counts = self.get_message_count()
        print(f"Total Messages (24h):     {counts['total']}")
        print(f"Cloud → Local:            {counts['cloud_to_local']}")
        print(f"Local → Cloud:            {counts['local_to_cloud']}")
        
        # Top topics
        print(f"\n🔝 TOP TOPICS:")
        top_topics = self.get_top_topics(5)
        for i, topic in enumerate(top_topics, 1):
            print(f"  {i}. {topic['topic']} ({topic['total_count']} messages)")
        
        # Module activity
        print(f"\n🏭 MODULE ACTIVITY:")
        module_activity = self.get_module_activity()
        for module, activity in module_activity.items():
            total = activity['cloud_to_local'] + activity['local_to_cloud']
            print(f"  {module}: {total} messages ({activity['cloud_to_local']} ↓, {activity['local_to_cloud']} ↑)")
        
        # Recent activity
        print(f"\n⏰ RECENT ACTIVITY:")
        recent = self.get_recent_messages(5)
        for msg in recent:
            timestamp = msg['timestamp'][:19]  # Remove microseconds
            print(f"  {timestamp} | {msg['direction']} | {msg['topic']}")
        
        print("="*80)
    
    def close(self):
        """Close database connection"""
        self.db_conn.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MQTT Traffic Analyzer")
    parser.add_argument("--db-file", default="mqtt_traffic.db", help="Database file path")
    parser.add_argument("--export-csv", help="Export to CSV file")
    parser.add_argument("--create-charts", action="store_true", help="Create visualization charts")
    parser.add_argument("--output-dir", default="traffic_analysis", help="Output directory for charts")
    parser.add_argument("--hours", type=int, default=24, help="Analysis period in hours")
    
    args = parser.parse_args()
    
    try:
        analyzer = MQTTTrafficAnalyzer(args.db_file)
        
        # Print summary
        analyzer.print_summary()
        
        # Export to CSV if requested
        if args.export_csv:
            analyzer.export_to_csv(args.export_csv)
        
        # Create charts if requested
        if args.create_charts:
            analyzer.create_visualizations(args.output_dir)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'analyzer' in locals():
            analyzer.close()

if __name__ == "__main__":
    main()
