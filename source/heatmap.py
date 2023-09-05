import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.animation import PillowWriter
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from scipy.stats import mode, linregress
import sys
from pathlib import Path
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



class Heatmap:
    def __init__(self):
        # SELECT FILE AUTOMATICALY; HAS BEEN REMOVED
        # if getattr(sys, 'frozen', False):
        #     # If the script is running as a bundled executable
        #     script_dir = Path(sys.executable).resolve().parent
        # else:
        #     # If the script is running as a regular Python script
        #     script_dir = Path(__file__).resolve().parent

        # # Find the CSV file in the script or executable directory
        # csv_files = list(script_dir.glob('*.csv'))
        # if not csv_files:
        #     raise FileNotFoundError("No CSV files found in the directory.")
        # csv_file = csv_files[0]
        # self.csv_file_name = str(csv_file).split('.')[0] # Storing the file name for later use
        # self.df = pd.read_csv(csv_file, sep=',', skiprows=range(0, 14), header=0, usecols=list(range(417, 673))).iloc[1:].astype(float)
        self.min = 28
        self.max = 45
        self.show_numbers = False  # Toggle numbers in cells

    def load_file(self, file_name):
        self.csv_file_name = str(file_name).split('.') # Storing the file name for later use
        self.df = pd.read_csv(file_name, sep=',', skiprows=range(0, 14), header=0, usecols=list(range(417, 673))).iloc[1:].astype(float)

    def set_scale(self, min_val, max_val):
        '''sets the scale of the plots (color sensivity) between two values entered in the params'''
        self.min = min_val
        self.max = max_val

    def set_scale_to_data(self, time=None):
        '''sets the scale of the plots (color sensivity) between the max and min of every sensor at a certain time (ignoring the zeros)'''
        if time is None:
            print("No time provided")
            return
        else:
            data = self.df.iloc[time].values
        data_non_zero = data[data > 5]  # ignore zeros
        self.min = np.nanmin(data_non_zero)
        self.max = np.nanmax(data_non_zero)

    def set_scale_to_avg(self, diff = 0):
        '''sets the scale of the plots (color sensivity) between the max and min on the average of every sensor, the scale can be enlarged a number in parameters'''
        data = self.df.mean().values
        data_non_zero = data[data > 5]  # ignore zeros        
        self.min = np.nanmin(data_non_zero) - diff
        self.max = np.nanmax(data_non_zero) + diff

    def _compute_common_stats(self, series_2D, row_offset=0, col_offset=0, ignore_zero=False):
        max_val = np.max(series_2D)
        min_val = np.min(series_2D)
        max_pos = np.unravel_index(np.argmax(series_2D), series_2D.shape)
        min_pos = np.unravel_index(np.argmin(series_2D), series_2D.shape)

        max_row = row_offset + max_pos[0]
        max_col = col_offset + max_pos[1]
        min_row = row_offset + min_pos[0]
        min_col = col_offset + min_pos[1]

        max_module = 8 - (max_col // 32)
        max_sensor = (max_col % 32) + 1
        min_module = 8 - (min_col // 32)
        min_sensor = (min_col % 32) + 1
        series = series_2D.flatten()
        print(mode(series).mode)
        stats = {
            "Average": np.mean(series),
            "Median": np.median(series),
            "Standard Deviation": np.std(series),
            "Root Mean Square": np.sqrt(np.mean(np.square(series))),
            "Minimum": {"value": min_val, "Module": min_module, "Sensor": min_sensor, "Time": min_row + 1},
            "Maximum": {"value": max_val, "Module": max_module, "Sensor": max_sensor, "Time": max_row + 1},
            "Q1": np.percentile(series, 25),
            "Q3": np.percentile(series, 75),
            "Percentiles": [np.percentile(series, p) for p in [25, 50, 75]],
            "Mode": [mode(series).mode][0] if [mode(series).count][0] > 0 else np.nan,
            "Variance": np.var(series),
            "Range": max_val - min_val,
            "Interquartile Range (IQR)": np.percentile(series, 75) - np.percentile(series, 25),
            "Max_Position": (max_row + 1, max_col + 1),
            "Min_Position": (min_row + 1, min_col + 1)
        }

        return stats

    def _compute_additional_stats(self, series_2D):
        # Linear regression from start to finish
        series = series_2D.flatten()
        y = series
        x = np.arange(len(y))
        slope, intercept, _, _, _ = linregress(x, y)
        additionnal_stats = str(f"Linear Regression (Start to Finish): y = {slope}x + {intercept}")

        # Linear regression from Q1 to Q3
        q1, q3 = np.percentile(y, [25, 75])
        mask = (y >= q1) & (y <= q3)
        slope, intercept, _, _, _ = linregress(x[mask], y[mask])
        additionnal_stats += str(f"\nLinear Regression (Q1 to Q3): y = {slope}x + {intercept}")

        # Quartile Means
        for p in [25, 50, 75]:
            quartile_data = y[(y >= np.percentile(y, p-5)) & (y <= np.percentile(y, p+5))]
            additionnal_stats += str(f"\nMean around {p}th percentile: {np.mean(quartile_data)}")
        return additionnal_stats

    def show_global_stats(self, ignore_zero=False):
        '''Display any revelant statistic about the entire DataSet'''
        df_numeric = self.df.apply(pd.to_numeric, errors='coerce')
        global_stats = self._compute_common_stats(df_numeric.values, ignore_zero)
        stats = ''
        stats += str("Global Stats:")
        for k, v in global_stats.items():
            stats += str(f"\n{k}: {v}")
        stats += "\n"
        # Max and Min Row Avg
        row_means = df_numeric.mean(axis=1)
        max_row_time = row_means.idxmax()
        min_row_time = row_means.idxmin()
        stats += str(f"\nHighest row average at time {max_row_time}: {row_means[max_row_time]}")
        stats += str(f"\nLowest row average at time {min_row_time}: {row_means[min_row_time]}")
        
        # Max and Min Col Avg
        col_means = df_numeric.mean()
        max_col = col_means.idxmax()
        min_col = col_means.idxmin()
        stats += str(f"\nHighest column average at column {max_col}: {col_means[max_col]}")
        stats += str(f"\nLowest column average at column {min_col}: {col_means[min_col]}")
        
        # Min and Max Module Average
        module_means = [df_numeric.iloc[:, i:i+32].mean().mean() for i in range(0, df_numeric.shape[1], 32)]
        max_module = np.argmax(module_means)
        min_module = np.argmin(module_means)
        stats += str(f"\nHighest module average in module {8 - max_module}: {module_means[max_module]}")
        stats += str(f"\nLowest module average in module {8 - min_module}: {module_means[min_module]}")
        return stats

    def show_time_stats(self, time, ignore_zero=False):
        '''Display any revelant statistic about a certain time in the DataSet''' 
        row_data = self.df.iloc[time:time+1, :]
        row_offset = time  # Row offset is the time index in this case
        col_offset = 0     # Column offset is 0 for a full row
        stats = ''
        stats += str(f"Time {time} Stats:")
        time_stats = self._compute_common_stats(row_data.values, row_offset=time, ignore_zero=ignore_zero)
        for k, v in time_stats.items():
            stats += str(f"\n{k}: {v}")
        stats += "\n"
        stats += str('\n' + self._compute_additional_stats(row_data.values))
        return stats

    def show_module_stats(self, module, ignore_zero=False):
        '''Display any revelant statistic about a certain module in the DataSet, includes data of the front, the back, and the entire module''' 
        # Existing code for slicing data remains the same
        front_start = (8 - module) * 32
        front_end = front_start + 16
        back_start = front_end
        back_end = back_start + 16
        
        front_data = self.df.iloc[:, front_start:front_end]
        back_data = self.df.iloc[:, back_start:back_end]
        module_data = self.df.iloc[:, front_start:back_end]
        # Front data starts from front_start column, so col_offset is front_start
        stats = ''
        stats += str(f"Front of Module {module} Stats:")
        front_stats = self._compute_common_stats(front_data.values, col_offset=front_start, ignore_zero=ignore_zero)
        for k, v in front_stats.items():
            stats += str(f"\n{k}: {v}")
        stats += "\n"
        # Back data starts from back_start column, so col_offset is back_start
        stats += str(f"\nBack of Module {module} Stats:")
        back_stats = self._compute_common_stats(back_data.values, col_offset=back_start, ignore_zero=ignore_zero)
        for k, v in back_stats.items():
            stats += str(f"\n{k}: {v}")
        stats += "\n"
        # Sensor data starts from front_start column, so col_offset is front_start
        stats += str(f"\nEntire Module {module} Stats:")
        module_stats = self._compute_common_stats(module_data.values, col_offset=front_start, ignore_zero=ignore_zero)
        for k, v in module_stats.items():
            stats += str(f"\n{k}: {v}")
        return stats


    def show_sensor_stats(self, module, sensor, ignore_zero=False):
        '''Display any revelant statistic about a certain sensor in the DataSet''' 
        sensor_col = (8 - module) * 32 + sensor - 1
        sensor_data = self.df.iloc[:, sensor_col:sensor_col+1]
        
        sensor_stats = self._compute_common_stats(sensor_data.values, col_offset=sensor_col, ignore_zero=ignore_zero)
        stats = ''
        stats += str(f"Stats for Module {module}, Sensor {sensor} (overall sensor {sensor_col + 1}):")
        for k, v in sensor_stats.items():
            stats += str(f"\n{k}: {v}")
        stats += "\n"
        stats += str('\n'+self._compute_additional_stats(sensor_data.values))
        return stats


    def _update_axes_data(self, ax, data, module):
        pattern = [
            [1, 0, 6, 9, 0, 14],
            [0, 4, 0, 0, 12, 0],
            [2, 0, 7, 10, 0, 15],
            [0, 5, 0, 0, 13, 0],
            [3, 0, 8, 11, 0, 16]
        ]
        heat_map_array = np.full((5, 6), np.nan)
        for i in range(5):
            for j in range(6):
                module_idx = pattern[i][j]
                if module_idx != 0:
                    heat_map_array[i, j] = data[module * 16 + module_idx - 1]

        # I have to do it 5 times for some weird ass reason
        for artist in ax.texts:
            artist.remove()
        for artist in ax.texts:
            artist.remove()
        for artist in ax.texts:
            artist.remove()
        for artist in ax.texts:
            artist.remove()
        for artist in ax.texts:
            artist.remove()
           
        cax = ax.images[0]
        cax.set_data(heat_map_array)
        cax.set_clim(self.min, self.max)
        if self.show_numbers:
            for i in range(5):
                for j in range(6):
                    val = heat_map_array[i, j]
                    if not np.isnan(val):
                        x = cax.get_extent()[0] + (j + 0.5) * (cax.get_extent()[1] - cax.get_extent()[0]) / 6
                        y = cax.get_extent()[3] - (i + 0.5) * (cax.get_extent()[3] - cax.get_extent()[2]) / 5
                        ax.text(x, y, f"{val:.1f}", fontsize=8, ha='center', va='center')

    def _create_plot_framework(self):
        fig, axs = plt.subplots(2, 8, figsize=(16, 6))
        cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
        
        # Add a blank image to each axis initially
        for ax in axs.flatten():
            ax.imshow([[0]], cmap='hot_r', interpolation='nearest', vmin=self.min, vmax=self.max)
            ax.tick_params(bottom=False, left=False)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
        
     
        plt.subplots_adjust(wspace=0.0, hspace=0.0)
        plt.tight_layout()
        return fig, axs, cbar_ax

    def show_time(self, axs=None, time = None):
        if axs is None:
            fig, axs, cbar_ax = self._create_plot_framework()
        else:
            fig = axs[0, 0].get_figure()
            cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])

        if time is None:
            avg_data = self.df.mean().values
            title = "Average"
            data = avg_data
        else:
            title = f"Time: {time}"
            data = self.df.iloc[time].values

        count = 0
        for module in range(16):
            ax = axs[count % 2, count // 2]
            self._update_axes_data(ax, data, module)
            ax.set_title(f"Module_{8 - module//2}_{count%2+1}", fontsize=8)
            count += 1

        fig.suptitle(title)
        cax = axs[0, 0].images[0]
        cbar = fig.colorbar(cax, cax=cbar_ax, orientation='horizontal')
        
        return fig, axs
    
    def toggle_numbers(self, toggle):
        ''' Enter True to show the temperature inside each cells, False to not see them, False is by default'''
        self.show_numbers = toggle

    # def show_average(self, fig=None, axs=None):
    #     avg_data = self.df.mean().values
    #     fig, axs = self._show_frame(title="Average", data=avg_data, fig=fig, axs=axs)
    #     return fig, axs
    
    def verify_columns(self):
        '''Display the columns that aren't accuratly places in the csv file'''
        column_names = self.df.columns.tolist()
        print(column_names)
        print("\n")
        print(self.df)
        count = 0
        for x in column_names:
            verify_module = 8-count//32
            verify_sensor = count % 32 + 1
            count +=1
            module = int(x[11])
            sensor = int(x[18:])

            if module != verify_module or sensor != verify_sensor:
                print(x, verify_module, verify_sensor)
    
    

   


