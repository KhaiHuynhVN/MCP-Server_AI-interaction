import argparse
import sys
from ai_interaction_tool.engine import run_persistent_ui

def main():
    """Main entry point for AI Interaction Tool"""
    parser = argparse.ArgumentParser(
        description="AI Interaction Tool - Advanced interface for AI communication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py --ui              Launch persistent UI mode
    python -m ai_interaction_tool --ui    Alternative launch method
        """
    )
    
    parser.add_argument(
        '--ui', '--persistent', 
        action='store_true',
        help='Launch persistent UI mode (keeps running in background)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='AI Interaction Tool v2.0 - Persistent Mode'
    )
    
    args = parser.parse_args()
    
    if args.ui:
        print("🚀 Launching AI Interaction Tool in Persistent Mode...")
        print("📌 UI will stay open for continuous agent communication")
        print("💡 Use 'Minimize' button to run in background")
        print("⚠️  Keep this terminal open while UI is running")
        print("-" * 60)
        
        try:
            # Launch persistent UI
            return run_persistent_ui()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down AI Interaction Tool...")
            return 0
        except Exception as e:
            print(f"❌ Error launching persistent UI: {e}")
            return 1
    else:
        # Show help if no arguments provided
        parser.print_help()
        print("\n💡 Tip: Use --ui to launch persistent UI mode")
        return 0


if __name__ == "__main__":
    sys.exit(main())
