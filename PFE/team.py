import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import ttk, font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.widgets import Cursor
import threading
import time
import os
import requests
from pathlib import Path

class TeamBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Premier League Team Builder")
        self.root.geometry("1600x1000")
        
        # Set theme and configure styles
        self.style = ttk.Style("flatly")
        self.setup_fonts()
        self.configure_styles()
        
        # Load and process data
        self.load_data()
        
        # Create main container with padding
        self.main_container = ttk.Frame(root, padding="20")
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Create header
        self.create_header()
        
        # Create main content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Create controls frame
        self.create_controls_frame()
        
        # Create results frame
        self.create_results_frame()
        
        # Configure grid weights for responsive layout
        self.content_frame.columnconfigure(1, weight=3)
        self.content_frame.rowconfigure(0, weight=1)
        
    def setup_fonts(self):
        # Download Poppins font if not present
        font_dir = Path("fonts")
        font_path = font_dir / "Poppins-Regular.ttf"
        
        if not font_path.exists():
            print("Downloading Poppins font...")
            font_url = "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"
            response = requests.get(font_url)
            font_path.write_bytes(response.content)
        
        # Load custom font
        self.custom_font = font.Font(family="Poppins", size=10)
        self.title_font = font.Font(family="Poppins", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Poppins", size=12)
        self.header_font = font.Font(family="Poppins", size=14, weight="bold")
        
        # Configure matplotlib to use Poppins
        plt.rcParams['font.family'] = 'Poppins'
        plt.rcParams['font.size'] = 10

    def configure_styles(self):
        # Configure ttkbootstrap styles
        self.style.configure(
            "TLabel",
            font=self.custom_font,
            padding=5
        )
        
        self.style.configure(
            "TButton",
            font=self.custom_font,
            padding=10
        )
        
        self.style.configure(
            "TCombobox",
            font=self.custom_font,
            padding=5
        )
        
        self.style.configure(
            "Treeview",
            font=self.custom_font,
            rowheight=30
        )
        
        self.style.configure(
            "Treeview.Heading",
            font=self.header_font
        )
        
        self.style.configure(
            "TLabelframe.Label",
            font=self.header_font
        )

    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="Premier League Team Builder",
            font=self.title_font
        )
        title_label.pack(side=LEFT)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Build your optimal team based on tactics and formation",
            font=self.subtitle_font
        )
        subtitle_label.pack(side=LEFT, padx=10)
        
    def create_controls_frame(self):
        self.controls_frame = ttk.LabelFrame(
            self.content_frame,
            text="Team Configuration",
            padding="20"
        )
        self.controls_frame.grid(row=0, column=0, padx=10, sticky=NSEW)
        
        # Tactic selection
        tactic_frame = ttk.Frame(self.controls_frame)
        tactic_frame.pack(fill=X, pady=10)
        
        ttk.Label(
            tactic_frame,
            text="Select Tactic:",
            font=self.header_font
        ).pack(anchor=W)
        
        self.tactic_var = tk.StringVar(value="balanced")
        self.tactic_combo = ttk.Combobox(
            tactic_frame,
            textvariable=self.tactic_var,
            values=list(self.tactics.keys()),
            state="readonly",
            width=20
        )
        self.tactic_combo.pack(fill=X, pady=5)
        ToolTip(
            self.tactic_combo,
            text="Choose your team's playing style:\n"
                 "• Possession: Focus on ball control and passing\n"
                 "• Counterattack: Quick transitions and direct play\n"
                 "• Balanced: Equal emphasis on all aspects"
        )
        
        # Formation selection
        formation_frame = ttk.Frame(self.controls_frame)
        formation_frame.pack(fill=X, pady=10)
        
        ttk.Label(
            formation_frame,
            text="Select Formation:",
            font=self.header_font
        ).pack(anchor=W)
        
        self.formation_var = tk.StringVar(value="4-3-3")
        self.formation_combo = ttk.Combobox(
            formation_frame,
            textvariable=self.formation_var,
            values=["4-3-3", "3-5-2", "4-4-2", "4-2-3-1", "3-4-3"],
            state="readonly",
            width=20
        )
        self.formation_combo.pack(fill=X, pady=5)
        ToolTip(
            self.formation_combo,
            text="Choose your team's formation:\n"
                 "• 4-3-3: Attacking formation with wingers\n"
                 "• 3-5-2: Strong midfield presence\n"
                 "• 4-4-2: Classic balanced formation\n"
                 "• 4-2-3-1: Modern attacking formation\n"
                 "• 3-4-3: Offensive formation with wing-backs"
        )
        
        # Player Filters
        filter_frame = ttk.LabelFrame(
            self.controls_frame,
            text="Player Filters",
            padding="10"
        )
        filter_frame.pack(fill=X, pady=10)
        
        # Age Range
        age_frame = ttk.Frame(filter_frame)
        age_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            age_frame,
            text="Age Range:",
            font=self.custom_font
        ).pack(side=LEFT, padx=5)
        
        self.min_age_var = tk.StringVar(value="18")
        self.max_age_var = tk.StringVar(value="40")
        
        ttk.Entry(
            age_frame,
            textvariable=self.min_age_var,
            width=5
        ).pack(side=LEFT, padx=2)
        
        ttk.Label(
            age_frame,
            text="to",
            font=self.custom_font
        ).pack(side=LEFT, padx=2)
        
        ttk.Entry(
            age_frame,
            textvariable=self.max_age_var,
            width=5
        ).pack(side=LEFT, padx=2)
        
        # Nationality Filter
        nationality_frame = ttk.Frame(filter_frame)
        nationality_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            nationality_frame,
            text="Nationality:",
            font=self.custom_font
        ).pack(side=LEFT, padx=5)
        
        self.nationality_var = tk.StringVar()
        self.nationality_combo = ttk.Combobox(
            nationality_frame,
            textvariable=self.nationality_var,
            values=["Any"] + sorted(self.df['Nation'].unique().tolist()),
            state="readonly",
            width=15
        )
        self.nationality_combo.set("Any")
        self.nationality_combo.pack(side=LEFT, padx=5)
        
        # Club Filter
        club_frame = ttk.Frame(filter_frame)
        club_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            club_frame,
            text="Club:",
            font=self.custom_font
        ).pack(side=LEFT, padx=5)
        
        self.club_var = tk.StringVar()
        self.club_combo = ttk.Combobox(
            club_frame,
            textvariable=self.club_var,
            values=["Any"] + sorted(self.df['Team'].unique().tolist()),
            state="readonly",
            width=15
        )
        self.club_combo.set("Any")
        self.club_combo.pack(side=LEFT, padx=5)
        
        # Availability Filter
        availability_frame = ttk.Frame(filter_frame)
        availability_frame.pack(fill=X, pady=5)
        
        self.exclude_injured_var = tk.BooleanVar(value=False)
        self.exclude_suspended_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(
            availability_frame,
            text="Exclude Injured Players",
            variable=self.exclude_injured_var,
            style="Switch.TCheckbutton"
        ).pack(side=LEFT, padx=5)
        
        ttk.Checkbutton(
            availability_frame,
            text="Exclude Suspended Players",
            variable=self.exclude_suspended_var,
            style="Switch.TCheckbutton"
        ).pack(side=LEFT, padx=5)
        
        # Generate button with loading indicator
        self.generate_btn = ttk.Button(
            self.controls_frame,
            text="Generate Team",
            command=self.start_team_generation,
            style="primary.TButton",
            width=20
        )
        self.generate_btn.pack(pady=20)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(
            self.controls_frame,
            mode='indeterminate',
            length=200
        )
        
    def create_results_frame(self):
        self.results_frame = ttk.LabelFrame(
            self.content_frame,
            text="Team Results",
            padding="20"
        )
        self.results_frame.grid(row=0, column=1, padx=10, sticky=NSEW)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=BOTH, expand=YES)
        
        # Formation tab
        formation_tab = ttk.Frame(self.notebook)
        self.notebook.add(formation_tab, text="Formation")
        
        # Create matplotlib figure for formation
        self.fig_formation = Figure(figsize=(10, 7), facecolor='#2b2b2b')
        self.ax_formation = self.fig_formation.add_subplot(111)
        self.canvas_formation = FigureCanvasTkAgg(self.fig_formation, master=formation_tab)
        self.canvas_formation.get_tk_widget().pack(fill=BOTH, expand=YES, pady=10)
        
        # Add toolbar for formation plot
        toolbar_frame = ttk.Frame(formation_tab)
        toolbar_frame.pack(fill=X)
        toolbar = NavigationToolbar2Tk(self.canvas_formation, toolbar_frame)
        toolbar.update()
        
        # Performance tab
        performance_tab = ttk.Frame(self.notebook)
        self.notebook.add(performance_tab, text="Performance Analysis")
        
        # Create matplotlib figure for performance
        self.fig_performance = Figure(figsize=(10, 7), facecolor='#2b2b2b')
        self.ax_performance = self.fig_performance.add_subplot(111)
        self.canvas_performance = FigureCanvasTkAgg(self.fig_performance, master=performance_tab)
        self.canvas_performance.get_tk_widget().pack(fill=BOTH, expand=YES, pady=10)
        
        # Add toolbar for performance plot
        toolbar_frame_perf = ttk.Frame(performance_tab)
        toolbar_frame_perf.pack(fill=X)
        toolbar_perf = NavigationToolbar2Tk(self.canvas_performance, toolbar_frame_perf)
        toolbar_perf.update()
        
        # Team Details tab
        team_details_tab = ttk.Frame(self.notebook)
        self.notebook.add(team_details_tab, text="Team Details")
        
        # Team list in a scrolled frame
        list_frame = ScrolledFrame(team_details_tab)
        list_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        self.team_list = ttk.Treeview(
            list_frame,
            columns=("Player", "Position", "Score", "Gls", "Ast", "xG", "PrgP"),
            show="headings",
            height=10
        )
        
        # Configure columns
        self.team_list.heading("Player", text="Player")
        self.team_list.heading("Position", text="Position")
        self.team_list.heading("Score", text="Performance Score")
        self.team_list.heading("Gls", text="Goals")
        self.team_list.heading("Ast", text="Assists")
        self.team_list.heading("xG", text="Expected Goals")
        self.team_list.heading("PrgP", text="Progressive Passes")
        
        self.team_list.column("Player", width=200)
        self.team_list.column("Position", width=100)
        self.team_list.column("Score", width=150)
        self.team_list.column("Gls", width=100)
        self.team_list.column("Ast", width=100)
        self.team_list.column("xG", width=150)
        self.team_list.column("PrgP", width=150)
        
        self.team_list.pack(fill=BOTH, expand=YES)
        
        # Player Replacement tab
        replacement_tab = ttk.Frame(self.notebook)
        self.notebook.add(replacement_tab, text="Player Replacement")
        
        # Create split view for replacement tab
        replacement_frame = ttk.Frame(replacement_tab)
        replacement_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Left side - Current team
        current_team_frame = ttk.LabelFrame(replacement_frame, text="Current Team", padding="10")
        current_team_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        
        self.current_team_tree = ttk.Treeview(
            current_team_frame,
            columns=("Player", "Position", "Score"),
            show="headings",
            height=10
        )
        
        self.current_team_tree.heading("Player", text="Player")
        self.current_team_tree.heading("Position", text="Position")
        self.current_team_tree.heading("Score", text="Performance Score")
        
        self.current_team_tree.column("Player", width=150)
        self.current_team_tree.column("Position", width=100)
        self.current_team_tree.column("Score", width=150)
        
        self.current_team_tree.pack(fill=BOTH, expand=YES)
        
        # Right side - Similar players
        similar_players_frame = ttk.LabelFrame(replacement_frame, text="Similar Players", padding="10")
        similar_players_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(5, 0))
        
        self.similar_players_tree = ttk.Treeview(
            similar_players_frame,
            columns=("Player", "Position", "Score", "Similarity"),
            show="headings",
            height=10
        )
        
        self.similar_players_tree.heading("Player", text="Player")
        self.similar_players_tree.heading("Position", text="Position")
        self.similar_players_tree.heading("Score", text="Performance Score")
        self.similar_players_tree.heading("Similarity", text="Similarity")
        
        self.similar_players_tree.column("Player", width=150)
        self.similar_players_tree.column("Position", width=100)
        self.similar_players_tree.column("Score", width=150)
        self.similar_players_tree.column("Similarity", width=150)
        
        self.similar_players_tree.pack(fill=BOTH, expand=YES)
        
        # Add selection event handlers
        self.current_team_tree.bind('<<TreeviewSelect>>', self.on_current_player_select)
        self.similar_players_tree.bind('<<TreeviewSelect>>', self.on_similar_player_select)
        
        # Add replace button
        replace_button_frame = ttk.Frame(replacement_tab)
        replace_button_frame.pack(fill=X, padx=10, pady=5)
        
        self.replace_button = ttk.Button(
            replace_button_frame,
            text="Replace Selected Player",
            command=self.replace_selected_player,
            style="primary.TButton",
            state="disabled"
        )
        self.replace_button.pack(pady=10)

    def on_current_player_select(self, event):
        """Handle selection of a player from current team."""
        try:
            selected = self.current_team_tree.selection()
            if selected:
                # Get the selected player
                player_name = self.current_team_tree.item(selected[0])['values'][0]
                player = self.optimal_team[self.optimal_team['Player'] == player_name].iloc[0]
                
                # Get and display similar players
                similar_players = self.compute_similar_players(player)
                
                # Clear and update similar players tree
                self.similar_players_tree.delete(*self.similar_players_tree.get_children())
                
                if not similar_players.empty:
                    for _, similar_player in similar_players.iterrows():
                        self.similar_players_tree.insert("", "end", values=(
                            similar_player['Player'],
                            similar_player['Pos'],
                            f"{similar_player['performance_score']:.2f}",
                            f"{similar_player['similarity']:.2f}"
                        ))
                    
                    # Enable replace button
                    self.replace_button.configure(state="normal")
                else:
                    # Show message if no similar players found
                    ttk.Messagebox.show_warning(
                        title="No Similar Players",
                        message="No similar players found for the selected player.",
                        parent=self.root
                    )
        except Exception as e:
            print(f"Error in player selection: {e}")
            ttk.Messagebox.show_error(
                title="Error",
                message="An error occurred while finding similar players.",
                parent=self.root
            )

    def on_similar_player_select(self, event):
        """Handle selection of a similar player."""
        selected = self.similar_players_tree.selection()
        if selected:
            self.replace_button.configure(state="normal")
        else:
            self.replace_button.configure(state="disabled")

    def replace_selected_player(self):
        """Replace the selected player with the selected similar player."""
        current_selected = self.current_team_tree.selection()
        similar_selected = self.similar_players_tree.selection()
        
        if current_selected and similar_selected:
            # Get the players
            current_player_name = self.current_team_tree.item(current_selected[0])['values'][0]
            similar_player_name = self.similar_players_tree.item(similar_selected[0])['values'][0]
            
            # Get the current player's index in optimal_team
            current_player_idx = self.optimal_team[self.optimal_team['Player'] == current_player_name].index[0]
            
            # Get the similar player's data
            similar_player = self.df[self.df['Player'] == similar_player_name].iloc[0]
            
            # Replace the player in optimal_team
            self.optimal_team.loc[current_player_idx] = similar_player
            
            # Update all UI elements
            self.update_ui()
            
            # Show success message
            ttk.Messagebox.show_info(
                title="Player Replaced",
                message=f"Successfully replaced {current_player_name} with {similar_player_name}",
                parent=self.root
            )

    def update_replacement_tab(self):
        """Update the replacement tab with current team data."""
        # Clear current team tree
        self.current_team_tree.delete(*self.current_team_tree.get_children())
        
        # Add current team players
        for _, player in self.optimal_team.iterrows():
            self.current_team_tree.insert("", "end", values=(
                player['Player'],
                player['Pos'],
                f"{player['performance_score']:.2f}"
            ))
        
        # Clear similar players tree
        self.similar_players_tree.delete(*self.similar_players_tree.get_children())
        
        # Disable replace button
        self.replace_button.configure(state="disabled")

    def start_team_generation(self):
        # Disable generate button and show progress
        self.generate_btn.configure(state="disabled")
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Start team generation in a separate thread
        thread = threading.Thread(target=self.generate_team)
        thread.daemon = True
        thread.start()
        
    def generate_team(self):
        # Simulate some processing time
        time.sleep(1)
        
        # Get selected tactic and formation
        tactic_choice = self.tactic_var.get()
        formation = [int(num) for num in self.formation_var.get().split('-')]
        weights = self.tactics[tactic_choice]
        
        # Apply filters
        filtered_df = self.df.copy()
        
        # Age filter
        try:
            min_age = int(self.min_age_var.get())
            max_age = int(self.max_age_var.get())
            filtered_df = filtered_df[
                (filtered_df['Age'] >= min_age) & 
                (filtered_df['Age'] <= max_age)
            ]
        except ValueError:
            pass  # Invalid age range, ignore filter
        
        # Nationality filter
        if self.nationality_var.get() != "Any":
            filtered_df = filtered_df[filtered_df['Nation'] == self.nationality_var.get()]
        
        # Club filter
        if self.club_var.get() != "Any":
            filtered_df = filtered_df[filtered_df['Team'] == self.club_var.get()]
        
        # Availability filters
        if self.exclude_injured_var.get() and 'Injured' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Injured'] != True]
        
        if self.exclude_suspended_var.get() and 'Suspended' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Suspended'] != True]
        
        # Calculate performance scores
        filtered_df['performance_score'] = (
            filtered_df['Gls'] * weights['Gls'] +
            filtered_df['Ast'] * weights['Ast'] +
            filtered_df['xG'] * weights['xG'] +
            filtered_df['PrgP'] * weights['PrgP']
        )
        
        # Select team
        team = []
        positions_needed = {'GK': 1, 'DF': formation[0], 'MF': formation[1], 'FW': formation[2]}
        
        for pos, count in positions_needed.items():
            # Get all players for this position
            pos_players = filtered_df[filtered_df['pos_group'] == pos]
            
            if len(pos_players) < count:
                # Not enough players for this position, show warning
                self.root.after(0, lambda: self.show_warning(
                    f"Not enough {pos} players available with current filters. "
                    f"Please adjust filters or try a different formation."
                ))
                return
            
            # Sort by performance score
            pos_players = pos_players.sort_values('performance_score', ascending=False)
            
            # Take top 3 players for randomization
            top_players = pos_players.head(3)
            
            # Randomly select players from top performers
            selected_players = top_players.sample(n=min(count, len(top_players)))
            
            # If we need more players, add them from the remaining pool
            if len(selected_players) < count:
                remaining_players = pos_players[~pos_players.index.isin(selected_players.index)]
                additional_players = remaining_players.head(count - len(selected_players))
                selected_players = pd.concat([selected_players, additional_players])
            
            team.append(selected_players)
        
        self.optimal_team = pd.concat(team)
        
        # Update UI in the main thread
        self.root.after(0, self.update_ui)
        
    def update_ui(self):
        """Update all UI elements after team changes."""
        # Update team list
        self.create_team_list()
        
        # Update formation plot
        self.plot_formation([int(num) for num in self.formation_var.get().split('-')])
        
        # Update performance plot
        self.plot_performance()
        
        # Update replacement tab
        self.update_replacement_tab()
        
        # Re-enable generate button and hide progress
        self.generate_btn.configure(state="normal")
        self.progress.stop()
        self.progress.pack_forget()
        
    def plot_performance(self):
        self.ax_performance.clear()
        
        # Sort players by performance score
        sorted_team = self.optimal_team.sort_values('performance_score', ascending=True)
        
        # Create horizontal bar chart
        bars = self.ax_performance.barh(
            sorted_team['Player'],
            sorted_team['performance_score'],
            color='#375a7f'
        )
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            self.ax_performance.text(
                width + 0.1,
                bar.get_y() + bar.get_height()/2,
                f'{width:.2f}',
                va='center',
                fontfamily='Poppins'
            )
        
        # Customize plot
        self.ax_performance.set_title(
            'Player Performance Scores',
            color='white',
            pad=20,
            fontfamily='Poppins',
            fontsize=12
        )
        self.ax_performance.set_facecolor('#2b2b2b')
        self.ax_performance.tick_params(colors='white', labelsize=10)
        self.ax_performance.grid(True, linestyle='--', alpha=0.3)
        
        # Adjust layout
        self.fig_performance.tight_layout()
        self.canvas_performance.draw()

    def plot_formation(self, formation):
        self.ax_formation.clear()
        self.ax_formation.set_xlim(0, 10)
        self.ax_formation.set_ylim(0, 7)  # Increased height for better spacing
        self.ax_formation.axis('off')
        self.ax_formation.set_facecolor('#2b2b2b')
        
        # Draw football field
        field = patches.Rectangle((0, 0), 10, 7, facecolor='#1a472a', alpha=0.3)
        self.ax_formation.add_patch(field)
        
        # Draw center circle
        center_circle = patches.Circle((5, 3.5), 1, fill=False, color='white', alpha=0.5)
        self.ax_formation.add_patch(center_circle)
        
        # Draw center line
        self.ax_formation.plot([0, 10], [3.5, 3.5], color='white', alpha=0.5, linestyle='--')
        
        # Define formation positions with adjusted y-coordinates
        if formation == [4, 3, 3]:
            formation_positions = {
                'GK': [(5, 0.5)],
                'DF': [(2, 1.5), (4, 1.5), (6, 1.5), (8, 1.5)],
                'MF': [(3, 3.5), (5, 3.5), (7, 3.5)],
                'FW': [(2, 5.5), (5, 5.5), (8, 5.5)]
            }
        elif formation == [3, 5, 2]:
            formation_positions = {
                'GK': [(5, 0.5)],
                'DF': [(3, 1.5), (5, 1.5), (7, 1.5)],
                'MF': [(2, 3.5), (4, 3.5), (5, 3.5), (6, 3.5), (8, 3.5)],
                'FW': [(4, 5.5), (6, 5.5)]
            }
        elif formation == [4, 4, 2]:
            formation_positions = {
                'GK': [(5, 0.5)],
                'DF': [(2, 1.5), (4, 1.5), (6, 1.5), (8, 1.5)],
                'MF': [(2, 3.5), (4, 3.5), (6, 3.5), (8, 3.5)],
                'FW': [(4, 5.5), (6, 5.5)]
            }
        else:
            formation_positions = {
                'GK': [(5, 0.5)],
                'DF': [(2, 1.5), (4, 1.5), (6, 1.5), (8, 1.5)],
                'MF': [(3, 3.5), (5, 3.5), (7, 3.5)],
                'FW': [(2, 5.5), (5, 5.5), (8, 5.5)]
            }
        
        # Find top performer
        top_performer = self.optimal_team.loc[self.optimal_team['performance_score'].idxmax()]
        
        # Plot players
        for idx, player in self.optimal_team.iterrows():
            pos = player['pos_group']
            if formation_positions.get(pos):
                plot_x, plot_y = formation_positions[pos].pop(0)
                
                # Create player circle
                is_top_performer = player['Player'] == top_performer['Player']
                circle = patches.Circle(
                    (plot_x, plot_y),
                    0.5,  # Increased circle size
                    facecolor='#375a7f',
                    edgecolor='gold' if is_top_performer else 'white',
                    linewidth=2 if is_top_performer else 1
                )
                self.ax_formation.add_patch(circle)
                
                # Format player name and position
                name = player['Player']
                if len(name) > 15:  # Truncate long names
                    name = name[:12] + "..."
                
                # Add player name and position with dynamic font size
                fontsize = 8 if len(name) <= 10 else 7
                self.ax_formation.text(
                    plot_x, plot_y - 0.1,  # Adjusted y position
                    name,
                    ha='center', va='center',
                    fontsize=fontsize,
                    color='white',
                    fontfamily='Poppins'
                )
                
                # Add position below name
                self.ax_formation.text(
                    plot_x, plot_y + 0.1,  # Adjusted y position
                    f"({player['Pos']})",
                    ha='center', va='center',
                    fontsize=7,
                    color='white',
                    fontfamily='Poppins'
                )
                
                # Add star for top performer
                if is_top_performer:
                    # Create a star using multiple triangles
                    star_points = []
                    for i in range(5):
                        # Outer point
                        angle = i * 2 * np.pi / 5 - np.pi / 2
                        star_points.append((
                            plot_x + 0.4 * np.cos(angle),
                            plot_y + 0.8 + 0.4 * np.sin(angle)
                        ))
                        # Inner point
                        angle = (i + 0.5) * 2 * np.pi / 5 - np.pi / 2
                        star_points.append((
                            plot_x + 0.2 * np.cos(angle),
                            plot_y + 0.8 + 0.2 * np.sin(angle)
                        ))
                    
                    star = patches.Polygon(
                        star_points,
                        closed=True,
                        fill=True,
                        color='gold'
                    )
                    self.ax_formation.add_patch(star)
        
        self.ax_formation.set_title(
            f"Optimal Team - {self.tactic_var.get().capitalize()} Tactic - Formation {self.formation_var.get()}",
            color='white',
            pad=20,
            fontfamily='Poppins',
            fontsize=12
        )
        
        # Add cursor for tooltips
        cursor = Cursor(self.ax_formation, useblit=True, color='white', linewidth=1)
        
        # Add tooltip functionality
        def on_hover(event):
            if event.inaxes == self.ax_formation:
                for idx, player in self.optimal_team.iterrows():
                    pos = player['pos_group']
                    if formation_positions.get(pos):
                        # Get the position for this player
                        player_positions = formation_positions[pos]
                        if player_positions:  # Check if there are positions left
                            plot_x, plot_y = player_positions[0]
                            if abs(event.xdata - plot_x) < 0.5 and abs(event.ydata - plot_y) < 0.5:
                                tooltip_text = (
                                    f"Player: {player['Player']}\n"
                                    f"Position: {player['Pos']}\n"
                                    f"Performance Score: {player['performance_score']:.2f}\n"
                                    f"Goals: {player['Gls']:.1f}\n"
                                    f"Assists: {player['Ast']:.1f}\n"
                                    f"xG: {player['xG']:.2f}\n"
                                    f"Progressive Passes: {player['PrgP']:.1f}"
                                )
                                ToolTip(self.canvas_formation.get_tk_widget(), tooltip_text)
                                break
        
        self.canvas_formation.mpl_connect('motion_notify_event', on_hover)
        self.canvas_formation.draw()

    def show_warning(self, message):
        ttk.Messagebox.show_warning(
            title="Warning",
            message=message,
            parent=self.root
        )

    def load_data(self):
        # Load data
        file_path = r'C:\Prathamesh\Yewale\Prathamesh\VIT\sem 2\Projects\PFE\data.csv'
        self.df = pd.read_csv(file_path)
        self.df.fillna(0, inplace=True)
        
        # Position mapping
        position_map = {'DF': 'DF', 'MF': 'MF', 'FW': 'FW', 'GK': 'GK'}
        self.df['pos_group'] = self.df['Pos'].apply(lambda x: position_map.get(x, 'Unknown'))
        
        # Prepare data for clustering
        stats_cols = ['Gls', 'Ast', 'xG', 'PrgP']
        X = self.df[stats_cols]
        scaler = StandardScaler()
        self.X_scaled = scaler.fit_transform(X)
        
        # Apply clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        self.df['cluster'] = kmeans.fit_predict(self.X_scaled)
        
        # Define tactics
        self.tactics = {
            'possession': {'Gls': 0.2, 'Ast': 0.4, 'xG': 0.2, 'PrgP': 0.2},
            'counterattack': {'Gls': 0.4, 'Ast': 0.2, 'xG': 0.3, 'PrgP': 0.1},
            'balanced': {'Gls': 0.25, 'Ast': 0.25, 'xG': 0.25, 'PrgP': 0.25}
        }

    def compute_similar_players(self, player, n=5):
        """Compute similar players based on performance metrics."""
        try:
            # Get players from the same position group
            pos_players = self.df[self.df['pos_group'] == player['pos_group']].copy()
            
            # Select relevant stats for comparison
            stats = ['Gls', 'Ast', 'xG', 'PrgP']
            
            # Normalize the stats
            scaler = MinMaxScaler()
            normalized_stats = scaler.fit_transform(pos_players[stats])
            
            # Get the player's normalized stats
            player_stats = scaler.transform(player[stats].values.reshape(1, -1))
            
            # Compute cosine similarity
            similarities = cosine_similarity(player_stats, normalized_stats)[0]
            
            # Add similarity scores to the DataFrame
            pos_players['similarity'] = similarities
            
            # Sort by similarity and exclude the player themselves
            similar_df = pos_players[pos_players['Player'] != player['Player']]
            similar_df = similar_df.sort_values('similarity', ascending=False)
            
            # Calculate performance score for similar players
            similar_df['performance_score'] = (
                similar_df['Gls'] * self.tactics[self.tactic_var.get()]['Gls'] +
                similar_df['Ast'] * self.tactics[self.tactic_var.get()]['Ast'] +
                similar_df['xG'] * self.tactics[self.tactic_var.get()]['xG'] +
                similar_df['PrgP'] * self.tactics[self.tactic_var.get()]['PrgP']
            )
            
            return similar_df.head(n)
        except Exception as e:
            print(f"Error computing similar players: {e}")
            return pd.DataFrame()

    def show_similar_players(self, player):
        """Show a popup with similar players."""
        similar_players = self.compute_similar_players(player)
        
        # Create popup window
        popup = ttk.Toplevel(self.root)
        popup.title(f"Similar Players to {player['Player']}")
        popup.geometry("600x400")
        
        # Create frame for content
        content_frame = ttk.Frame(popup, padding="20")
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Show selected player info
        ttk.Label(
            content_frame,
            text=f"Selected Player: {player['Player']}",
            font=self.header_font
        ).pack(anchor=W, pady=(0, 10))
        
        # Create treeview for similar players
        similar_tree = ttk.Treeview(
            content_frame,
            columns=("Player", "Position", "Score", "Similarity"),
            show="headings",
            height=10
        )
        
        # Configure columns
        similar_tree.heading("Player", text="Player")
        similar_tree.heading("Position", text="Position")
        similar_tree.heading("Score", text="Performance Score")
        similar_tree.heading("Similarity", text="Similarity")
        
        similar_tree.column("Player", width=200)
        similar_tree.column("Position", width=100)
        similar_tree.column("Score", width=150)
        similar_tree.column("Similarity", width=150)
        
        similar_tree.pack(fill=BOTH, expand=YES, pady=10)
        
        # Add similar players to treeview
        for _, similar_player in similar_players.iterrows():
            similar_tree.insert("", "end", values=(
                similar_player['Player'],
                similar_player['Pos'],
                f"{similar_player['performance_score']:.2f}",
                f"{similar_player['similarity']:.2f}"
            ))
        
        # Add select button
        def replace_player():
            selected = similar_tree.selection()
            if selected:
                new_player = similar_players.iloc[similar_tree.index(selected[0])]
                self.replace_player_in_team(player, new_player)
                popup.destroy()
        
        ttk.Button(
            content_frame,
            text="Replace Player",
            command=replace_player,
            style="primary.TButton"
        ).pack(pady=10)

    def replace_player_in_team(self, old_player, new_player):
        """Replace a player in the team and update UI."""
        # Replace player in optimal_team
        self.optimal_team = self.optimal_team.replace(old_player, new_player)
        
        # Update UI
        self.update_ui()

    def create_team_list(self):
        """Create the team list with replace buttons."""
        # Clear existing items
        for item in self.team_list.get_children():
            self.team_list.delete(item)
        
        # Add players with replace buttons
        for idx, player in self.optimal_team.iterrows():
            values = (
                player['Player'],
                player['Pos'],
                f"{player['performance_score']:.2f}",
                f"{player['Gls']:.1f}",
                f"{player['Ast']:.1f}",
                f"{player['xG']:.2f}",
                f"{player['PrgP']:.1f}"
            )
            
            # Insert the player into the treeview
            self.team_list.insert("", "end", values=values)

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = TeamBuilderGUI(root)
    root.mainloop()