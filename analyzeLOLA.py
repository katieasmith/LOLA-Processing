import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

DataSetName = "sm10"
fin = False

# where to pull data from
path = "C:/Users/katie/Documents/LOLA_Software/bin/output/"

# where the output data will go 
output_path = "c:/Users/katie/Documents/LOLA_Software/"

# make folder for specific data set
output_path = os.path.join(output_path, DataSetName)
os.makedirs(output_path, exist_ok=True)

# make folder for intermediate data
int_dir = os.path.join(output_path, "IntPlots")
os.makedirs(int_dir, exist_ok=True)

# make folder for final figures
plt_dir = os.path.join(output_path, "Figures")
os.makedirs(plt_dir, exist_ok=True)

os.chdir(output_path)

def read_lola_file(filepath):
    """
    Read LOLA file and fix merged negative values in the data itself
    """
    import re
    
    # Read raw lines
    with open(filepath, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    # Fix lines where negative number is merged
    fixed_lines = []
    for line in lines:
        # Find pattern like "123.456-789.012" and add space: "123.456 -789.012"
        fixed_line = re.sub(r'(\d)(-\d)', r'\1 \2', line)
        fixed_lines.append(fixed_line)
    
    # Parse fixed data
    from io import StringIO
    df = pd.read_csv(
        StringIO(''.join(fixed_lines)),
        sep=r'\s+',
        engine='python'
    )
    return df

try:
    filenames = np.load('filenames.npy', allow_pickle = True)

    # valid (no flag) processed data
    filetitle = DataSetName + "_ValidData.gzip"
    data = pd.read_parquet(filetitle, engine='fastparquet')
    sclk = data['sclk']
    alt = data['alt']
    lon = data['lon']
    lat = data['lat']
    IDnum = data['ID']
    
    # all processed data
    filetitle = DataSetName + "_GroundTracks.gzip"
    data = pd.read_parquet(filetitle, engine='fastparquet')
    sclk_all = data['sclk']
    lon_all = data['lon']
    lat_all = data['lat']
    IDnum_all = data['ID']
    
except:
    filenames = []

    sclk = []
    alt = []
    lon = []
    lat = []
    IDnum = []

    sclk_all = []
    lon_all = []
    lat_all = []
    IDnum_all = []

# count of processed files
ct = len(filenames)

# count of skipped files
skipped_files = 0

# interval to plot data
plot_int = 50

# number of intervals of plot data
num_plot_int = 0

introduce = True

totalfiles = len(os.listdir(path))

for x in os.listdir(path):
    if x in filenames:
        # skipped file if 
        skipped_files +=1
    else:
        if introduce:
            print(f"Already Processed {skipped_files} Files")
            print(f"{totalfiles} Total Files")
        
        introduce = False
        
        filepath = os.path.join(path, x)
        df = read_lola_file(filepath)

        # full data (not filtered by flag)
        sclk_f = df.SCLK_LOLA
        alt_f = df.alt_km
        ID_f = df.id
        lon_f = df.longitudeE
        lat_f = df.latitudeN
        flg = df.flg
        
        sclk_all = np.concatenate((sclk_all, sclk_f), axis=0)
        lon_all = np.concatenate((lon_all, lon_f), axis=0)
        lat_all = np.concatenate((lat_all, lat_f), axis=0)
        IDnum_all = np.concatenate((IDnum_all, ID_f), axis=0)
        
        ind = np.where((flg == 0))[0]
        gdp = len(ind)
        bdp = len(flg)
        
        sclk = np.concatenate((sclk, sclk_f[ind]), axis=0)
        alt = np.concatenate((alt, alt_f[ind]), axis=0)
        lon = np.concatenate((lon, lon_f[ind]), axis=0)
        lat = np.concatenate((lat, lat_f[ind]), axis=0)
        IDnum = np.concatenate((IDnum, ID_f[ind]), axis=0)
        filenames = np.append(filenames, x)
        
        ct += 1
        
        print(f"Processed File {ct}/{totalfiles}: {x}")
         
        if np.mod(ct, plot_int) == 0:

            num_plot_int += 1
            
            n = 500
            plt.figure(figsize=(8, 5))
            plt.plot(lon_all[::n], lat_all[::n], 'o', markersize=0.25)
            plt.grid(True)
            plt.xlabel('Longitude [deg]')
            plt.ylabel('Latitude [deg]')
            plt.title(f'LOLA Ground Tracks (Every {n} pts): {ct} Files')
            plt.xlim((0, 360))
            plt.ylim((-90, 90))
            plt.savefig(os.path.join(int_dir, f"groundtracks_{ct}files.png"), dpi=150, bbox_inches='tight')
            plt.close()
            
            n = 100
            plt.figure(figsize=(8, 5))
            plt.plot(lon[::n], lat[::n], 'o', markersize=0.25)
            plt.grid(True)
            plt.xlabel('Longitude [deg]')
            plt.ylabel('Latitude [deg]')
            plt.title(f'Accepted Data Points (Every {n} pts): {ct} Files')
            plt.xlim((0, 360))
            plt.ylim((-90, 90))
            plt.savefig(os.path.join(int_dir, f"acceptedpts_{ct}files.png"), dpi=150, bbox_inches='tight')
            plt.close()

            plt.figure(figsize=(8, 4))
            n = 100
            plt.xlabel('Longitude [deg]')
            plt.ylabel('Latitude [deg]')
            plt.title(f'Elevation Contour (Every {n} pts): {ct} Files')
            plt.scatter(lon[::n], lat[::n], c=alt[::n], s=1, cmap='viridis')
            plt.colorbar(label='Altitude [km]')
            plt.xlim((0, 360))
            plt.ylim((-90, 90))
            plt.savefig(os.path.join(int_dir, f"elevationcont_{ct}files.png"), dpi=150, bbox_inches='tight')
            plt.close()
            
            perc = len(lon) / (len(lon_all)) * 100
            perc = round(perc)
            print(f"{ct} Files Processed")
            print(f"Valid Data = {perc}%")

np.save('filenames', filenames)

print('Saving Filtered Data...')
# Filtered Data
fn = DataSetName + "_ValidData.gzip"
d = {'sclk': sclk, 'alt': alt, 'lon': lon, 'lat': lat, 'ID': IDnum}
df = pd.DataFrame(data=d)
df.to_parquet(fn, engine="fastparquet", compression="gzip")

print('Saving Ground Track Data...')
# Full Ground Tracks
fn = DataSetName + "_GroundTracks.gzip"
d = {'sclk': sclk_all, 'lon': lon_all, 'lat': lat_all, 'ID': IDnum_all}
df = pd.DataFrame(data=d)
df.to_parquet(fn, engine="fastparquet", compression="gzip")

if fin:
    print('Saving Pole Data...')
    # Pole Data
    Nind = np.where((lat >= 80))[0]
    Nlat = lat[Nind]
    Nlon = lon[Nind]
    Nalt = alt[Nind]

    Sind = np.where((lat <= -80))[0]
    Slat = lat[Sind]
    Slon = lon[Sind]
    Salt = alt[Sind]

    fn = DataSetName + "_NP.gzip"
    d = {'Nlat': Nlat, 'Nlon': Nlon, 'Nalt': Nalt}
    df = pd.DataFrame(data=d)
    df.to_parquet(fn, engine="fastparquet", compression="gzip")

    fn = DataSetName + "_SP.gzip"
    d = {'Slat': Slat, 'Slon': Slon, 'Salt': Salt}
    df = pd.DataFrame(data=d)
    df.to_parquet(fn, engine="fastparquet", compression="gzip")

    print('Saving Shortened Data...')
    fn = DataSetName + "_Every100.gzip"
    n=100
    d = {'sclk': sclk[::n], 'alt': alt[::n], 'lon': lon[::n], 'lat': lat[::n], 'ID': IDnum[::n]}
    df = pd.DataFrame(data=d)
    df.to_parquet(fn, engine="fastparquet", compression="gzip")

    print("Plotting Ground Tracks...")

    n = 500
    plt.figure(figsize=(8, 5))
    plt.plot(lon_all[::n], lat_all[::n], 'o', markersize=0.25)
    plt.grid(True)
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title(f'LOLA Ground Tracks (Every {n} pts): {totalfiles} Files')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.savefig(os.path.join(plt_dir, DataSetName + f"GroundTracks.png"), dpi=150, bbox_inches='tight')
    plt.close()

    n = 100
    plt.figure(figsize=(8, 5))
    plt.plot(lon[::n], lat[::n], 'o', markersize=0.25)
    plt.grid(True)
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title(f'Accepted Data Points (Every {n} pts)')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.savefig(os.path.join(plt_dir, DataSetName + f"ValidData.png"), dpi=150, bbox_inches='tight')
    plt.close()

    perc = len(lon) / (len(lon_all)) * 100
    perc = round(perc)

    print("Plotting Contour Plots...")

    n = 10
    plt.figure(figsize=(8, 4))
    plt.scatter(lon[::n], lat[::n], c=alt[::n], s=1, cmap='viridis')
    plt.colorbar(label='Altitude [km]')
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title(f'Altitude Contour (Every 10 points): {perc}% of Data Valid')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.savefig(os.path.join(plt_dir, DataSetName + f"AltCont.png"), dpi=150, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(8, 4))
    n = 10
    plt.xlabel('Longitude [deg]')
    plt.ylabel('Latitude [deg]')
    plt.title('Elevation Contour (linear interpolation)')
    plt.tricontourf(lon[::n], lat[::n], alt[::n])
    plt.colorbar(label='Altitude [km]')
    plt.xlim((0, 360))
    plt.ylim((-90, 90))
    plt.savefig(os.path.join(plt_dir, DataSetName + f"AltCont_smooth.png"), dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Percentage of Accepted Data = {perc}")
    print(f"{DataSetName} Completed")

