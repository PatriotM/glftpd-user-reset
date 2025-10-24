#!/usr/bin/env python3
"""
glFTPD UserStat Reset v1.0 (Python Implementation)
Resets user statistics in glFTPD userfiles
"""

import os
import sys
import glob
import re
from datetime import datetime
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================
DEFAULT_GLFTPD_PATH = '/glftpd'
DEFAULT_USERFILE_DIR = 'ftp-data/users'
# ============================================================================

def reset_stats_line(line, reset_type):
    """Reset a specific stats line to zero"""
    if reset_type in line:
        # Extract the stat type and reset values
        parts = line.split()
        if len(parts) >= 4:
            # Format: STATTYPE files bytes time
            # Reset to: STATTYPE 0 0 0
            return f"{parts[0]} 0 0 0\n"
    return line

def process_userfile(userfile, reset_day=False, reset_week=False, reset_month=False, reset_all=False):
    """Process a single userfile and reset specified statistics"""
    try:
        with open(userfile, 'r') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        in_section = False
        
        for line in lines:
            # Track if we're inside a [SECTION]
            if '[SECTION]' in line:
                in_section = True
                new_lines.append(line)
                continue
            elif '[ENDSECTION]' in line:
                in_section = False
                new_lines.append(line)
                continue
            
            # Only reset stats inside [SECTION] blocks
            if in_section:
                original_line = line
                
                if reset_day and line.startswith('DAYUP '):
                    line = reset_stats_line(line, 'DAYUP')
                    modified = True
                elif reset_day and line.startswith('DAYDN '):
                    line = reset_stats_line(line, 'DAYDN')
                    modified = True
                elif reset_week and line.startswith('WKUP '):
                    line = reset_stats_line(line, 'WKUP')
                    modified = True
                elif reset_week and line.startswith('WKDN '):
                    line = reset_stats_line(line, 'WKDN')
                    modified = True
                elif reset_month and line.startswith('MONTHUP '):
                    line = reset_stats_line(line, 'MONTHUP')
                    modified = True
                elif reset_month and line.startswith('MONTHDN '):
                    line = reset_stats_line(line, 'MONTHDN')
                    modified = True
                elif reset_all and line.startswith('ALLUP '):
                    line = reset_stats_line(line, 'ALLUP')
                    modified = True
                elif reset_all and line.startswith('ALLDN '):
                    line = reset_stats_line(line, 'ALLDN')
                    modified = True
            
            new_lines.append(line)
        
        # Write back if modified
        if modified:
            with open(userfile, 'w') as f:
                f.writelines(new_lines)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {userfile}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='glFTPD UserStat Reset v1.0',
        add_help=False
    )
    
    parser.add_argument('-r', '--config', 
                       metavar='path',
                       help='Use Alternate Config file')
    parser.add_argument('-e', '--monday',
                       action='store_true',
                       help='Reset on Monday versus Sunday')
    parser.add_argument('-d', '--day',
                       action='store_true',
                       help="Reset Today's Stats Only")
    parser.add_argument('-w', '--week',
                       action='store_true',
                       help='Reset Week Stats Only')
    parser.add_argument('-m', '--month',
                       action='store_true',
                       help='Reset Month Stats Only')
    parser.add_argument('-a', '--alltime',
                       action='store_true',
                       help='Reset Alltime Stats Only')
    parser.add_argument('-h', '-?', '--help',
                       action='store_true',
                       help='This Help Screen')
    
    args = parser.parse_args()
    
    # Show help
    if args.help:
        print("glFTPD UserStat Reset v1.0")
        print("Options:")
        print("  -r {path}    Use Alternate Config file.")
        print("  -e           Reset on Monday versus Sunday.")
        print("  -d           Reset Today's Stats Only.")
        print("  -w           Reset Week Stats Only.")
        print("  -m           Reset Month Stats Only.")
        print("  -a           Reset Alltime Stats Only.")
        print("  -h/?         This Help Screen")
        sys.exit(0)
    
    # Default config path
    if args.config:
        glftpd_path = os.path.dirname(args.config)
    else:
        glftpd_path = DEFAULT_GLFTPD_PATH
    
    userfile_dir = os.path.join(glftpd_path, DEFAULT_USERFILE_DIR)
    
    if not os.path.exists(userfile_dir):
        print(f"Error: User directory not found: {userfile_dir}")
        print(f"Please specify the correct path with -r option")
        sys.exit(1)
    
    # Determine what to reset
    reset_day = args.day
    reset_week = args.week
    reset_month = args.month
    reset_all = args.alltime
    
    # If no specific reset specified, determine based on date
    if not any([reset_day, reset_week, reset_month, reset_all]):
        now = datetime.now()
        reset_week_day = 0 if args.monday else 6  # Monday=0, Sunday=6
        
        reset_day = True  # Always reset day
        
        if now.weekday() == reset_week_day:
            reset_week = True
            print("Weekly reset triggered")
            
        if now.day == 1:
            reset_month = True
            print("Monthly reset triggered")
    
    # Get all userfiles
    userfiles = []
    for item in os.listdir(userfile_dir):
        filepath = os.path.join(userfile_dir, item)
        if os.path.isfile(filepath):
            userfiles.append(filepath)
    
    if not userfiles:
        print(f"No userfiles found in {userfile_dir}")
        sys.exit(1)
    
    print(f"Processing {len(userfiles)} userfiles...")
    success_count = 0
    
    for userfile in userfiles:
        if process_userfile(userfile, reset_day, reset_week, reset_month, reset_all):
            success_count += 1
    
    print(f"Successfully reset stats in {success_count} userfiles")
    
    # Print what was reset
    reset_items = []
    if reset_day:
        reset_items.append("Day")
    if reset_week:
        reset_items.append("Week")
    if reset_month:
        reset_items.append("Month")
    if reset_all:
        reset_items.append("Alltime")
    
    if reset_items:
        print(f"Reset: {', '.join(reset_items)} statistics")

if __name__ == '__main__':
    main()
