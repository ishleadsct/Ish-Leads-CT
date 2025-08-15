#!/usr/bin/env python3
"""
Ultra AI Client v1.0 - Interactive Interface
Samsung Galaxy S24 Ultra (Termux) Edition
HTTP-based client for communicating with the aiohttp API server.
"""

import asyncio
import sys
import time
from pathlib import Path
import json

try:
    import aiohttp
except ImportError:
    print("❌ aiohttp library not found. Please install it:")
    print("   pip install aiohttp")
    sys.exit(1)

# Color codes for enhanced terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
WHITE = '\033[1;37m'
GRAY = '\033[0;37m'
NC = '\033[0m'  # No Color

class UltraAIClient:
    def __init__(self, server_url: str = "http://127.0.0.1:8765/api"):
        self.server_url = server_url
        self.session = None

    def print_banner(self):
        """Display Ultra AI client banner"""
        print(f"{CYAN}")
        print("██╗   ██╗██╗  ████████╗██████╗  █████╗      █████╗ ██╗")
        print("██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗    ██╔══██╗██║")
        print("██║   ██║██║     ██║   ██████╔╝███████║    ███████║██║")
        print("██║   ██║██║     ██║   ██╔══██╗██╔══██║    ██╔══██║██║")
        print("╚██████╔╝███████╗██║   ██║  ██║██║  ██║    ██║  ██║██║")
        print(" ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝")
        print(f"{NC}")
        print(f"{WHITE}Ultra AI v1.0 Client - Samsung Galaxy S24 Ultra Edition{NC}")
        print(f"{BLUE}Metric-Based Intelligence • Dynamic Memory Management{NC}")
        print(f"{GRAY}Connected to server via HTTP API at {self.server_url}{NC}")
        print()

    async def create_session(self):
        """Create a single aiohttp client session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close the aiohttp client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def send_query(self, query: str, dive_confirmed: bool = False) -> dict:
        """Send query to server and receive JSON response"""
        payload = {
            "text": query,
            "dive_confirmed": dive_confirmed
        }
        
        try:
            async with self.session.post(self.server_url, json=payload, timeout=300) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"status": "error", "message": f"Server error: {resp.status}"}
        except aiohttp.ClientConnectorError:
            return {"status": "error", "message": "Failed to connect to server. Is the server running?"}
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Request timed out."}
        except Exception as e:
            return {"status": "error", "message": f"Communication error: {e}"}

    def print_help(self):
        """Display help information"""
        print(f"\n{CYAN}Ultra AI Client Commands:{NC}")
        print(f"  {WHITE}help{NC}      - Show this help message")
        print(f"  {WHITE}clear{NC}     - Clear the screen")
        print(f"  {WHITE}exit{NC}      - Exit the client")
        print(f"  {WHITE}quit{NC}      - Exit the client")
        print(f"  {WHITE}bye{NC}       - Exit the client")
        print()
        print(f"{BLUE}Tips:{NC}")
        print(f"  • Ultra AI uses metric-based intelligence to select optimal models")
        print(f"  • Complex queries automatically activate specialist models") 
        print(f"  • The system manages GPU/CPU allocation dynamically")
        print(f"  • Memory is managed intelligently for S24 Ultra performance")
        print()

    def format_response(self, response: str) -> str:
        """Format and enhance response display"""
        if not response:
            return f"{RED}No response received{NC}"
        
        # Add some visual enhancement
        lines = response.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue
                
            # Highlight code blocks (simple detection)
            if any(keyword in line.lower() for keyword in ['def ', 'import ', 'class ', 'function', '```']):
                formatted_lines.append(f"{BLUE}{line}{NC}")
            # Highlight important information
            elif line.startswith('Important:') or line.startswith('Note:'):
                formatted_lines.append(f"{YELLOW}{line}{NC}")
            # Regular text
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    async def run_interactive_loop(self):
        """Main interactive loop"""
        self.print_banner()
        await self.create_session()
        
        print(f"{GREEN}🎯 Ultra AI is ready! Type 'help' for commands.{NC}")
        print()

        try:
            while True:
                try:
                    # Get user input
                    query = input(f"{PURPLE}Ultra AI>{NC} ").strip()
                    
                    if not query:
                        continue
                    
                    # Handle special commands
                    if query.lower() in ['exit', 'quit', 'bye']:
                        print(f"{BLUE}👋 Goodbye!{NC}")
                        break
                    elif query.lower() == 'help':
                        self.print_help()
                        continue
                    elif query.lower() == 'clear':
                        print('\033[2J\033[H', end='')  # Clear screen
                        continue
                    
                    # Send query to server
                    print(f"{GRAY}🤔 Processing...{NC}")
                    start_time = time.time()
                    
                    response_json = await self.send_query(query)
                    
                    processing_time = time.time() - start_time
                    
                    # Handle different server response statuses
                    if response_json.get("status") == "needs_deeper":
                        print(f"{YELLOW}💭 {response_json.get('prompt')}{NC}")
                        deeper_choice = input(f"{PURPLE}Dive Deeper? (y/n)>{NC} ").strip().lower()
                        if deeper_choice == 'y':
                            print(f"{GRAY}🤔 Diving deeper...{NC}")
                            start_time = time.time()
                            response_json = await self.send_query(query, dive_confirmed=True)
                            processing_time = time.time() - start_time
                        else:
                            print(f"{BLUE}Okay, stopping.{NC}")
                            continue
                            
                    # Display response
                    if response_json.get("status") == "ok":
                        answer = response_json.get("answer")
                        print(f"\n{GREEN}🎯 Ultra AI Response:{NC}")
                        print("─" * 60)
                        print(self.format_response(answer))
                        print("─" * 60)
                        print(f"{GRAY}⏱️  Processed in {processing_time:.2f} seconds{NC}")
                    elif response_json.get("status") == "error":
                        print(f"{RED}❌ Error: {response_json.get('message')}{NC}")
                    else:
                        print(f"{RED}❌ Unexpected response from server:{NC}")
                        print(json.dumps(response_json, indent=2))
                    
                    print()  # Add spacing
                    
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}⚠️  Interrupted. Type 'exit' to quit.{NC}")
                    continue
                except EOFError:
                    print(f"\n{BLUE}👋 Goodbye!{NC}")
                    break
                except Exception as e:
                    print(f"{RED}❌ Error: {e}{NC}")
                    
        finally:
            await self.close_session()

async def main_async():
    """Main client function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultra AI Client v9.0")
    parser.add_argument(
        "--server", 
        default="http://127.0.0.1:8765/api",
        help="URL of the API server (default: http://127.0.0.1:8765/api)"
    )
    parser.add_argument(
        "--query",
        help="Single query mode - send one query and exit"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        global RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, WHITE, GRAY, NC
        RED = GREEN = YELLOW = BLUE = PURPLE = CYAN = WHITE = GRAY = NC = ""
    
    client = UltraAIClient(args.server)
    await client.create_session()

    if args.query:
        # Single query mode
        response_json = await client.send_query(args.query)
        if response_json.get("status") == "ok":
            print(client.format_response(response_json.get("answer")))
        elif response_json.get("status") == "needs_deeper":
            # In single query mode, we assume confirmation
            response_json = await client.send_query(args.query, dive_confirmed=True)
            if response_json.get("status") == "ok":
                print(client.format_response(response_json.get("answer")))
            else:
                print(f"Error: {response_json.get('message', 'Unknown')}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: {response_json.get('message', 'Unknown')}", file=sys.stderr)
            sys.exit(1)
        
    else:
        # Interactive mode
        try:
            await client.run_interactive_loop()
        except KeyboardInterrupt:
            print(f"\n{BLUE}👋 Goodbye!{NC}")
            
    await client.close_session()


if __name__ == "__main__":
    asyncio.run(main_async())