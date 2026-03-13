# ============================================
# OPTIK PLATFORM - MCP SERVERS
# ============================================
# 
# Model Context Protocol (MCP) servers for e-commerce integration:
# - Universal E-commerce MCP Server
# - WooCommerce MCP Server
# ============================================

from .universal_ecommerce_mcp_server import UniversalEcommerceMCPServer
from .woocommerce_mcp_server import WooCommerceMCPServer

__all__ = [
    'UniversalEcommerceMCPServer',
    'WooCommerceMCPServer'
]

__version__ = "1.0.0"
__description__ = "Optik Platform MCP Servers"
