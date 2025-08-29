#!/usr/bin/env python3
"""
Secure Configuration Loader für Orbis Modellfabrik
Orbis Development - Sichere Verwaltung von Credentials
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecureConfigLoader:
    """Sicherer Config-Loader für sensitive Daten"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.credentials_file = self.config_dir / "credentials.yml"
        self.example_file = self.config_dir / "credentials.example.yml"

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        logger.info("Secure Config Loader initialized")
        logger.info(f"Config directory: {self.config_dir}")

    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """Lade Credentials sicher"""
        try:
            if not self.credentials_file.exists():
                logger.warning(f"Credentials file not found: {self.credentials_file}")
                logger.info(
                    f"Please copy {self.example_file} to {self.credentials_file} and fill in your credentials"
                )
                return None

            # Check file permissions (should be 600)
            stat = self.credentials_file.stat()
            if stat.st_mode & 0o777 != 0o600:
                logger.warning(
                    f"Credentials file has insecure permissions: {oct(stat.st_mode)}"
                )
                logger.info(
                    "Consider setting permissions to 600: chmod 600 config/credentials.yml"
                )

            with open(self.credentials_file, "r") as f:
                credentials = yaml.safe_load(f)

            logger.info("✅ Credentials loaded successfully")
            return credentials

        except yaml.YAMLError as e:
            logger.error(f"Error parsing credentials file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None

    def get_mqtt_config(self) -> Optional[Dict[str, Any]]:
        """Hole MQTT-Konfiguration"""
        credentials = self.load_credentials()
        if not credentials:
            return None

        mqtt_config = credentials.get("mqtt", {})

        # Validate required fields
        required_fields = ["broker"]
        for field in required_fields:
            if field not in mqtt_config:
                logger.error(f"Missing required MQTT field: {field}")
                return None

        return mqtt_config

    def get_ccu_config(self) -> Optional[Dict[str, Any]]:
        """Hole CCU-Konfiguration"""
        credentials = self.load_credentials()
        if not credentials:
            return None

        return credentials.get("ccu", {})

    def get_network_config(self) -> Optional[Dict[str, Any]]:
        """Hole Netzwerk-Konfiguration"""
        credentials = self.load_credentials()
        if not credentials:
            return None

        return credentials.get("network", {})

    def validate_credentials(self) -> bool:
        """Validiere Credentials"""
        credentials = self.load_credentials()
        if not credentials:
            return False

        # Check required sections
        required_sections = ["network", "mqtt", "ccu"]
        for section in required_sections:
            if section not in credentials:
                logger.error(f"Missing required section: {section}")
                return False

        # Check MQTT configuration
        mqtt_config = credentials["mqtt"]
        if "broker" not in mqtt_config:
            logger.error("Missing MQTT broker configuration")
            return False

        # Check CCU configuration
        ccu_config = credentials["ccu"]
        if "ssh" not in ccu_config:
            logger.error("Missing CCU SSH configuration")
            return False

        logger.info("✅ Credentials validation passed")
        return True

    def create_example_config(self) -> bool:
        """Erstelle Beispiel-Konfiguration"""
        try:
            if self.example_file.exists():
                logger.info(f"Example file already exists: {self.example_file}")
                return True

            # Create example content
            example_content = """# 🔐 Orbis Modellfabrik - Credentials Configuration
# Copy this file to credentials.yml and fill in your actual credentials
# NEVER commit credentials.yml to version control!

# APS Modellfabrik Network Configuration
network:
  aps_ip: "192.168.0.100"
  network_range: "192.168.0.0/24"
  gateway: "192.168.0.1"
  dns: "192.168.0.1"

# Raspberry Pi Access
raspberry_pi:
  hostname: "192.168.0.100"
  ssh:
    username: "pi"
    password: "raspberry"  # Change this!
    port: 22
    enabled: true

# MQTT Broker Configuration
mqtt:
  broker:
    host: "192.168.0.100"
    port: 1883
    ssl: false
    keepalive: 60
  
  authentication:
    enabled: true
    username: ""  # Fill in when discovered
    password: ""  # Fill in when discovered
  
  topics:
    - "module/v1/ff/#"
    - "fischertechnik/#"
    - "aps/#"
    - "#"

# Development Environment
development:
  local_mqtt:
    host: "localhost"
    port: 1883
    authentication: false

# Security Settings
security:
  change_default_passwords: true
  enable_firewall: true
  restrict_ssh_access: true
  use_ssl: false

# Status
status:
  last_updated: "2025-08-14"
  version: "1.0"
  tested: false
  production_ready: false
"""

            with open(self.example_file, "w") as f:
                f.write(example_content)

            logger.info(f"✅ Example config created: {self.example_file}")
            return True

        except Exception as e:
            logger.error(f"Error creating example config: {e}")
            return False

    def print_security_guidelines(self):
        """Zeige Sicherheitsrichtlinien"""
        print("\n🔐 SECURITY GUIDELINES")
        print("=" * 50)
        print("1. NEVER commit credentials.yml to version control")
        print("2. Set file permissions to 600: chmod 600 config/credentials.yml")
        print("3. Change all default passwords")
        print("4. Use strong, unique passwords")
        print("5. Enable SSL/TLS for production")
        print("6. Restrict network access with firewalls")
        print("7. Regularly update credentials")
        print("8. Monitor access logs")
        print("9. Use environment variables for sensitive data")
        print("10. Implement role-based access control")
        print("=" * 50)


def main():
    """Hauptfunktion"""
    print("🔐 Secure Config Loader für Orbis Modellfabrik")
    print("=" * 50)

    loader = SecureConfigLoader()

    # Create example config if needed
    if not loader.example_file.exists():
        print("📝 Creating example configuration...")
        loader.create_example_config()

    # Try to load credentials
    print("🔍 Loading credentials...")
    credentials = loader.load_credentials()

    if credentials:
        print("✅ Credentials loaded successfully")

        # Validate credentials
        print("🔍 Validating credentials...")
        if loader.validate_credentials():
            print("✅ Credentials validation passed")

            # Show MQTT config
            mqtt_config = loader.get_mqtt_config()
            if mqtt_config:
                print(
                    f"📡 MQTT Broker: {mqtt_config['broker']['host']}:{mqtt_config['broker']['port']}"
                )

            # Show network config
            network_config = loader.get_network_config()
            if network_config:
                print(f"🌐 CCU IP: {network_config['ccu_ip']}")
                print(f"📡 MQTT Port: {network_config['mqtt_port']}")
        else:
            print("❌ Credentials validation failed")
    else:
        print("❌ No credentials found")
        print("💡 Please copy config/credentials.example.yml to config/credentials.yml")
        print("💡 Then fill in your actual credentials")

    # Show security guidelines
    loader.print_security_guidelines()


if __name__ == "__main__":
    main()
