"""
Gateway Factory - Zentral für die Erzeugung/Verwaltung von Singleton-Clients und Gateways

Bietet Factory-Methoden für alle Domänen-Gateways:
- CcuGateway
- NoderedGateway  
- AdminGateway

Implementiert das Factory-Pattern für thread-sichere Gateway-Erstellung.
"""

import threading
from typing import Optional, Dict, Any
from omf2.common.logger import get_logger

logger = get_logger(__name__)


class GatewayFactory:
    """
    Factory für die Erzeugung und Verwaltung von Singleton-Gateways
    
    Thread-sichere Factory, die sicherstellt, dass pro Domäne nur eine
    Gateway-Instanz existiert.
    """
    
    _instance: Optional['GatewayFactory'] = None
    _lock = threading.Lock()
    _gateways: Dict[str, Any] = {}
    _gateway_locks: Dict[str, threading.Lock] = {}
    
    def __new__(cls) -> 'GatewayFactory':
        """Singleton-Pattern für GatewayFactory"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._gateways = {}
                    cls._instance._gateway_locks = {}
                    logger.info("🏭 GatewayFactory Singleton initialized")
        return cls._instance
    
    def get_ccu_gateway(self, **kwargs) -> 'CcuGateway':
        """
        Factory-Methode für CcuGateway
        
        Args:
            **kwargs: Konfigurationsparameter für CcuGateway
            
        Returns:
            CcuGateway: Singleton-Instanz des CCU Gateways
        """
        gateway_name = "ccu"
        
        if gateway_name not in self._gateway_locks:
            self._gateway_locks[gateway_name] = threading.Lock()
        
        with self._gateway_locks[gateway_name]:
            if gateway_name not in self._gateways:
                from omf2.ccu.ccu_gateway import CcuGateway
                self._gateways[gateway_name] = CcuGateway(**kwargs)
                logger.info(f"🏭 Created {gateway_name} gateway")
            
            return self._gateways[gateway_name]
    
    def get_nodered_gateway(self, **kwargs) -> 'NoderedGateway':
        """
        Factory-Methode für NoderedGateway
        
        Args:
            **kwargs: Konfigurationsparameter für NoderedGateway
            
        Returns:
            NoderedGateway: Singleton-Instanz des Node-RED Gateways
        """
        gateway_name = "nodered"
        
        if gateway_name not in self._gateway_locks:
            self._gateway_locks[gateway_name] = threading.Lock()
        
        with self._gateway_locks[gateway_name]:
            if gateway_name not in self._gateways:
                from omf2.nodered.nodered_gateway import NoderedGateway
                self._gateways[gateway_name] = NoderedGateway(**kwargs)
                logger.info(f"🏭 Created {gateway_name} gateway")
            
            return self._gateways[gateway_name]
    
    def get_admin_gateway(self, **kwargs) -> 'AdminGateway':
        """
        Factory-Methode für AdminGateway
        
        Args:
            **kwargs: Konfigurationsparameter für AdminGateway
            
        Returns:
            AdminGateway: Singleton-Instanz des Admin Gateways
        """
        gateway_name = "admin"
        
        if gateway_name not in self._gateway_locks:
            self._gateway_locks[gateway_name] = threading.Lock()
        
        with self._gateway_locks[gateway_name]:
            if gateway_name not in self._gateways:
                from omf2.admin.admin_gateway import AdminGateway
                self._gateways[gateway_name] = AdminGateway(**kwargs)
                logger.info(f"🏭 Created {gateway_name} gateway")
            
            return self._gateways[gateway_name]
    
    def get_gateway(self, domain: str, **kwargs) -> Any:
        """
        Generische Factory-Methode für alle Gateways
        
        Args:
            domain: Domäne ('ccu', 'nodered', 'admin')
            **kwargs: Konfigurationsparameter
            
        Returns:
            Gateway: Entsprechende Gateway-Instanz
            
        Raises:
            ValueError: Bei unbekannter Domäne
        """
        if domain == 'ccu':
            return self.get_ccu_gateway(**kwargs)
        elif domain == 'nodered':
            return self.get_nodered_gateway(**kwargs)
        elif domain == 'admin':
            return self.get_admin_gateway(**kwargs)
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    def get_all_gateways(self) -> Dict[str, Any]:
        """
        Gibt alle erstellten Gateways zurück
        
        Returns:
            Dict[str, Any]: Dictionary mit allen Gateway-Instanzen
        """
        return self._gateways.copy()
    
    def reset_gateway(self, domain: str) -> None:
        """
        Setzt ein Gateway zurück (für Tests)
        
        Args:
            domain: Domäne zum Zurücksetzen
        """
        if domain in self._gateways:
            with self._gateway_locks.get(domain, threading.Lock()):
                if domain in self._gateways:
                    del self._gateways[domain]
                    logger.info(f"🏭 Reset {domain} gateway")
    
    def reset_all_gateways(self) -> None:
        """
        Setzt alle Gateways zurück (für Tests)
        """
        with self._lock:
            self._gateways.clear()
            logger.info("🏭 Reset all gateways")


# Factory-Instanz
_gateway_factory = None
_factory_lock = threading.Lock()


def get_gateway_factory() -> GatewayFactory:
    """
    Factory-Funktion für GatewayFactory Singleton
    
    Returns:
        GatewayFactory: Singleton-Instanz der Gateway Factory
    """
    global _gateway_factory
    
    if _gateway_factory is None:
        with _factory_lock:
            if _gateway_factory is None:
                _gateway_factory = GatewayFactory()
                logger.info("🏭 GatewayFactory factory function initialized")
    
    return _gateway_factory


# Convenience-Funktionen für direkten Gateway-Zugriff
def get_ccu_gateway(**kwargs) -> 'CcuGateway':
    """Convenience-Funktion für CcuGateway"""
    return get_gateway_factory().get_ccu_gateway(**kwargs)


def get_nodered_gateway(**kwargs) -> 'NoderedGateway':
    """Convenience-Funktion für NoderedGateway"""
    return get_gateway_factory().get_nodered_gateway(**kwargs)


def get_admin_gateway(**kwargs) -> 'AdminGateway':
    """Convenience-Funktion für AdminGateway"""
    return get_gateway_factory().get_admin_gateway(**kwargs)


def get_gateway(domain: str, **kwargs) -> Any:
    """Convenience-Funktion für generischen Gateway-Zugriff"""
    return get_gateway_factory().get_gateway(domain, **kwargs)
