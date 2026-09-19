import argparse
import logging

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from akshare_one_mcp.server import mcp

logger = logging.getLogger(__name__)


def create_streamable_http_app():
    app = mcp.http_app()
    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id", "mcp-protocol-version"],
        max_age=86400,
    )
    return app


def main():
    parser = argparse.ArgumentParser(description="akshare-one MCP Server")
    parser.add_argument(
        "--streamable-http",
        action="store_true",
        help="Use streamable HTTP mode instead of stdio",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8081, help="Port to listen on (default: 8081)"
    )

    args = parser.parse_args()

    if args.streamable_http:
        # HTTP mode for streamable HTTP
        print("MCP Server starting in HTTP mode...")
        app = create_streamable_http_app()
        print(f"Listening on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port, log_level="debug")
    else:
        # stdio mode (default)
        print("MCP Server starting in stdio mode...")
        mcp.run()


if __name__ == "__main__":
    main()
