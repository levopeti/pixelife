"""
Main entry point for artificial life simulation
Handles program initialization, main loop, and save/load
"""

import sys
import argparse
import os
from world import World
from simulation import Simulation
from statistics import Statistics
from visualization import Visualization
from save_manager import SaveManager
import config

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Artificial Life Simulation')
    parser.add_argument('--width', type=int, default=config.WORLD_WIDTH,
                       help='World width')
    parser.add_argument('--height', type=int, default=config.WORLD_HEIGHT,
                       help='World height')
    parser.add_argument('--load', type=str, default=None,
                       help='Load a saved simulation (filename)')
    
    args = parser.parse_args()
    
    # Create save manager
    save_manager = SaveManager()
    
    # Load existing simulation or create new one
    if args.load:
        print(f"Loading simulation from: {args.load}")
        result = save_manager.load_simulation(args.load)
        if result:
            world, statistics = result
            print("Simulation loaded successfully!")
        else:
            print("Failed to load simulation. Starting new one.")
            world = World(args.width, args.height)
            statistics = Statistics()
    else:
        # Create new world
        print(f"Initializing new world ({args.width}x{args.height})...")
        world = World(args.width, args.height)
        statistics = Statistics()
    
    # Create simulation
    print("Creating simulation...")
    simulation = Simulation(world, statistics)
    
    # Create visualization
    print("Starting visualization...")
    print("\n=== CONTROLS ===")
    print("F key: Toggle between FAST mode and VISUAL mode")
    print("Space: Pause/unpause (visual mode only)")
    print("WASD/Arrows: Pan camera (visual mode)")
    print("Mouse wheel: Zoom (visual mode)")
    print("1-9: Change speed (visual mode)")
    print("Ctrl+S: Save simulation")
    print("Ctrl+L: Load simulation")
    print("================\n")
    
    visualization = Visualization(world, statistics)
    
    # Auto-save tracking
    last_autosave_tick = 0
    
    # Main loop
    running = True
    while running and simulation.running:
        # Handle events
        event_result = visualization.handle_events()
        
        if event_result == False:
            running = False
        elif event_result == 'save':
            print("\nSaving simulation...")
            save_manager.save_simulation(world, statistics)
            print("Save complete!\n")
        elif event_result == 'load':
            print("\n=== Available Saves ===")
            saves = save_manager.list_saves()
            if saves:
                for i, save in enumerate(saves):
                    print(f"{i+1}. {save['filename']} - {save['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print("\nEnter filename to load (or press Enter to cancel):")
                filename = input("> ").strip()
                if filename:
                    result = save_manager.load_simulation(filename)
                    if result:
                        world, statistics = result
                        # Recreate simulation with loaded data
                        simulation = Simulation(world, statistics)
                        visualization.world = world
                        visualization.statistics = statistics
                        print("Simulation loaded!\n")
            else:
                print("No saves found.")
        
        # Render if needed (always in visual mode, occasionally in fast mode)
        if visualization.should_render():
            visualization.render()
        
        # Update simulation (not if paused in visual mode)
        if not (visualization.paused and not visualization.fast_mode):
            ticks_to_run = visualization.get_ticks_per_frame()
            for _ in range(ticks_to_run):
                simulation.update()
        
        # Auto-save
        if statistics.ticks - last_autosave_tick >= config.AUTO_SAVE_INTERVAL:
            print(f"\nAuto-saving at tick {statistics.ticks}...")
            save_manager.save_simulation(world, statistics, "autosave.save")
            last_autosave_tick = statistics.ticks
        
        # Tick clock
        visualization.tick()
    
    # Final save offer
    print("\n\nSimulation ended.")
    print(f"Final tick: {statistics.ticks}")
    print(f"Final population: {statistics.creature_count}")
    print("\nWould you like to save before exiting? (y/n)")
    
    try:
        response = input("> ").strip().lower()
        if response == 'y':
            save_manager.save_simulation(world, statistics)
            print("Simulation saved!")
    except:
        pass
    
    print("\n=== Final Statistics ===")
    statistics.print_summary()
    print("\nGoodbye!")

if __name__ == "__main__":
    main()

