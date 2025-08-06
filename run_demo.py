#!/usr/bin/env python3
"""
Quick Start Demo Runner

This script provides an easy way to run the different demos and see the
value proposition of MCP servers for retailers.
"""

import subprocess
import sys
import os

def print_banner():
    """Print the demo banner"""
    print("🏪" + "=" * 78 + "🏪")
    print("🏪                WAYFAIR MCP SERVER PROTOTYPE DEMO                🏪")
    print("🏪" + "=" * 78 + "🏪")
    print()
    print("This prototype demonstrates how retailers can enhance AI agent")
    print("experiences by providing structured access to their product data")
    print("through MCP (Model Context Protocol) servers.")
    print()

def show_menu():
    """Show the demo menu"""
    print("📋 Available Demos:")
    print("1. Current State Demo (ChatGPT limitations)")
    print("2. Enhanced State Demo (ChatGPT with MCP)")
    print("3. Side-by-Side Comparison")
    print("4. Start MCP Server")
    print("5. Run All Demos")
    print("6. Exit")
    print()

def run_current_demo():
    """Run the current state demo"""
    print("\n🚫 Running Current State Demo...")
    print("This shows ChatGPT's limitations without MCP access.\n")
    
    try:
        subprocess.run([sys.executable, "demo_current_state.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running current state demo: {e}")
    except FileNotFoundError:
        print("❌ demo_current_state.py not found")

def run_enhanced_demo():
    """Run the enhanced state demo"""
    print("\n✅ Running Enhanced State Demo...")
    print("This shows ChatGPT's capabilities with MCP server access.\n")
    
    try:
        subprocess.run([sys.executable, "demo_enhanced_state.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running enhanced state demo: {e}")
    except FileNotFoundError:
        print("❌ demo_enhanced_state.py not found")

def run_comparison_demo():
    """Run the comparison demo"""
    print("\n📊 Running Side-by-Side Comparison...")
    print("This shows the before and after scenarios.\n")
    
    try:
        subprocess.run([sys.executable, "compare_demos.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running comparison demo: {e}")
    except FileNotFoundError:
        print("❌ compare_demos.py not found")

def start_mcp_server():
    """Start the MCP server"""
    print("\n🚀 Starting MCP Server...")
    print("The server will be available at http://localhost:8000")
    print("API documentation at http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        subprocess.run([sys.executable, "wayfair_mcp_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting MCP server: {e}")
    except FileNotFoundError:
        print("❌ wayfair_mcp_server.py not found")
    except KeyboardInterrupt:
        print("\n🛑 MCP Server stopped.")

def run_all_demos():
    """Run all demos in sequence"""
    print("\n🎬 Running All Demos...")
    print("This will show the complete value proposition.\n")
    
    # Run current state demo
    run_current_demo()
    
    print("\n" + "=" * 80)
    print("⏸️  Press Enter to continue to Enhanced State Demo...")
    input()
    
    # Run enhanced state demo
    run_enhanced_demo()
    
    print("\n" + "=" * 80)
    print("⏸️  Press Enter to continue to Comparison Demo...")
    input()
    
    # Run comparison demo
    run_comparison_demo()
    
    print("\n" + "=" * 80)
    print("✅ All demos completed!")
    print("💡 You can now start the MCP server to test the API directly.")

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        "demo_current_state.py",
        "demo_enhanced_state.py", 
        "compare_demos.py",
        "wayfair_mcp_server.py",
        "product_data.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   • {file}")
        print("\nPlease ensure all files are present in the current directory.")
        return False
    
    return True

def main():
    """Main demo runner"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Select a demo (1-6): ").strip()
            
            if choice == "1":
                run_current_demo()
            elif choice == "2":
                run_enhanced_demo()
            elif choice == "3":
                run_comparison_demo()
            elif choice == "4":
                start_mcp_server()
            elif choice == "5":
                run_all_demos()
            elif choice == "6":
                print("\n👋 Thanks for exploring the Wayfair MCP Server prototype!")
                print("💡 Remember: MCP servers are the future of AI agent integration.")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
            
            if choice in ["1", "2", "3", "5"]:
                print("\n" + "=" * 80)
                print("⏸️  Press Enter to return to menu...")
                input()
        
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Thanks for exploring!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 