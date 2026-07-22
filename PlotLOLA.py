import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import mpl_scatter_density
import matplotlib.patches
import matplotlib.path as mpath

lunar_elevation = LinearSegmentedColormap.from_list('lunar_elevation', [
    (0.000, '#8C00C0'),   # -9150 m  deep purple
    (0.125, '#1A33E5'),   # -5168 m  blue
    (0.250, '#00D9F2'),   # -1186 m  cyan
    (0.375, '#4DE84D'),   #  2796 m  green
    (0.500, '#FFD700'),   #  4787 m  yellow
    (0.625, '#FF7300'),   # ~6500 m  orange
    (0.875, '#D90000'),   #  8769 m  red
    (1.000, '#FFFFFF'),   # 10760 m  white
], N=256)


data = pd.read_parquet('Every100pt_full.gzip', engine='fastparquet')
alt = data['alt']
lon = data['lon']
lat = data['lat']
sclk = data['sclk']
ID = data['ID']


"""
------------------------------------------------
PLOT DATA FROM ALL DIRECTORIES
------------------------------------------------
"""

mainplot = False

if mainplot:    
    
    print("Plotting Contour Plot...")
    n = 1
    plt.figure(figsize=(8, 5))    
    plt.scatter(lon[::n], lat[::n], c=alt[::n], s=1, cmap='viridis')
    plt.colorbar(label='Altitude [km]')
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title('Altitude Contour Plot')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.show()
    


"""
------------------------------------------------
PLOT HEAT MAP FOR DATA POINTS
------------------------------------------------
"""   

heatmap = False

if heatmap:
    
    print("Plotting Heat Map...")
    fig = plt.figure(figsize=(8, 5))    
    ax = fig.add_subplot(1, 1, 1, projection='scatter_density')
    density = ax.scatter_density(lon, lat, cmap='hot')
    fig.colorbar(density, label='Number of points per pixel')
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title('Valid Data Density Plot')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.show()



# ============================================================================
# FILTER FOR POLAR REGIONS
# ============================================================================

poleplot = True

if poleplot:
    
    data = pd.read_parquet('SouthPoleData_full.gzip', engine='fastparquet')
    alt_south = data['alt']
    lon_south = data['lon']
    lat_south = data['lat']
    
    data = pd.read_parquet('NorthPoleData_full.gzip', engine='fastparquet')
    alt_north = data['alt']
    lon_north = data['lon']
    lat_north = data['lat']
    
    deg2rad = np.pi / 180  
    
    # ============================================================================
    # PLOT NORTH POLE
    # ============================================================================
    
    print("Plotting North Pole...")
    
    if len(lat_north) > 0:
        # Polar stereographic: distance from pole
        r_north = 90 - lat_north  # Distance from north pole (0 at pole, 10 at 80°)
        theta_north = lon_north * deg2rad  # Angle in radians
        
        # Convert to Cartesian
        x_north = r_north * np.cos(theta_north)
        y_north = r_north * np.sin(theta_north)
        
        print(f"\nNorth Pole: {len(lat_north):,} points")
        print(f"  Latitude range: {lat_north.min():.1f}° to {lat_north.max():.1f}°")
        print(f"  Altitude range: {alt_north.min():.1f} to {alt_north.max():.1f} km")
        
        # Plot 1: Scatter plot
        plt.figure()
        n = 100 #max(1, len(x_north) // 10000)  # Subsample if too many points
        plt.scatter(x_north[::n], y_north[::n], c=alt_north[::n], s=1, cmap='viridis')
        plt.colorbar(label='Altitude [km]')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title(f'North Polar Region (>{lat_north.min():.0f}°N)')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.xlim((-11,11))
        #plt.ylim((-11,11))
        #plt.tight_layout()
        plt.show()
        
        # Plot 2: Contour plot
        plt.figure()
        n = 100 #max(1, len(x_north) // 5000)  # Subsample for faster contour
        plt.tricontourf(x_north[::n], y_north[::n], alt_north[::n], levels=20, cmap='viridis')
        plt.colorbar(label='Altitude [km]')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title(f'North Polar Elevation Map (every {n} points)')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.ylim((-11,11))
        #plt.xlim((-11,11))
        plt.show()
        
        # Plot 3: Density Map
        n = 100
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection='scatter_density')
        density = ax.scatter_density(x_north[::n], y_north[::n], cmap='hot')
        fig.colorbar(density, label='Number of points per pixel')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title('North Pole: Valid Data Density Plot')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.ylim((-11,11))
        #plt.xlim((-11,11))
        cx = 0
        cy = 0
        r = 10
        circle = matplotlib.patches.Circle((cx,cy), r, transform=ax.transData)
        density.set_clip_path(circle)
        # Create a large rectangle with a circular hole using Path
        theta = np.linspace(0, 2 * np.pi, 300)
        circle_verts = np.column_stack([cx + r * np.cos(theta), cy + r * np.sin(theta)])
        # Outer rectangle (must be larger than the plot)
        rect_verts = np.array([[-100, -100], [100, -100], [100, 100], [-100, 100], [-100, -100]])
        # Combine: rectangle path + reversed circle path (creates a hole)
        verts = np.concatenate([rect_verts, circle_verts[::-1]])
        codes = (
            [mpath.Path.MOVETO] + [mpath.Path.LINETO] * 4 +
            [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(circle_verts) - 1)
        )
        mask_path = mpath.Path(verts, codes)
        mask_patch = matplotlib.patches.PathPatch(mask_path, facecolor='white', edgecolor='black',
                                         linewidth=1.5, transform=ax.transData, zorder=5)
        ax.add_patch(mask_patch)
        plt.show()
        
    # ============================================================================
    # PLOT SOUTH POLE
    # ============================================================================
    
    print("Plotting South Pole...")
    
    if len(lat_south) > 0:
        # Polar stereographic: distance from pole
        r_south = 90 + lat_south  # Distance from south pole (lat is negative)
        theta_south = lon_south * deg2rad
        
        # Convert to Cartesian
        x_south = r_south * np.cos(theta_south)
        y_south = r_south * np.sin(theta_south)
        
        print(f"\nSouth Pole: {len(lat_south):,} points")
        print(f"  Latitude range: {lat_south.min():.1f}° to {lat_south.max():.1f}°")
        print(f"  Altitude range: {alt_south.min():.1f} to {alt_south.max():.1f} km")
        
        # Plot 1: Scatter plot
        plt.figure()
        n = 100 #max(1, len(x_south) // 10000)
        plt.scatter(x_south[::n], y_south[::n], c=alt_south[::n], s=1, cmap='viridis')
        plt.colorbar(label='Altitude [km]')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title(f'South Polar Region (<{lat_south.max():.0f}°S)')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.ylim((-11,11))
        #plt.xlim((-11,11))
        #plt.tight_layout()
        plt.show()
        
        # Plot 2: Contour plot
        plt.figure()
        n = 100 # max(1, len(x_south) // 5000)
        plt.tricontourf(x_south[::n], y_south[::n], alt_south[::n], levels=20, cmap='viridis')
        plt.colorbar(label='Altitude [km]')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title(f'South Polar Elevation Map (every {n} points)')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.ylim((-11,11))
        #plt.xlim((-11,11))
        #plt.tight_layout()
        plt.show()
        
        # Plot 3: Density Map
        n = 100
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection='scatter_density')
        density = ax.scatter_density(x_south[::n], y_south[::n], cmap='hot')
        fig.colorbar(density, label='Number of points per pixel')
        plt.xlabel('X (East-West)')
        plt.ylabel('Y (North-South)')
        plt.title('South Pole: Valid Data Density Plot')
        plt.axis('equal')
        plt.grid(True, alpha=0.3)
        plt.xlim((-11,11))
        #plt.ylim((-11,11))
        cx = 0
        cy = 0
        r = 10
        circle = matplotlib.patches.Circle((cx,cy), r, transform=ax.transData)
        density.set_clip_path(circle)
        # Create a large rectangle with a circular hole using Path
        theta = np.linspace(0, 2 * np.pi, 300)
        circle_verts = np.column_stack([cx + r * np.cos(theta), cy + r * np.sin(theta)])
        # Outer rectangle (must be larger than the plot)
        rect_verts = np.array([[-100, -100], [100, -100], [100, 100], [-100, 100], [-100, -100]])
        # Combine: rectangle path + reversed circle path (creates a hole)
        verts = np.concatenate([rect_verts, circle_verts[::-1]])
        codes = (
            [mpath.Path.MOVETO] + [mpath.Path.LINETO] * 4 +
            [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(circle_verts) - 1)
        )
        mask_path = mpath.Path(verts, codes)
        mask_patch = matplotlib.patches.PathPatch(mask_path, facecolor='white', edgecolor='black',
                                         linewidth=1.5, transform=ax.transData, zorder=5)
        ax.add_patch(mask_patch)
        plt.show()
