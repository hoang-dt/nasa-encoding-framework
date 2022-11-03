# DYAMOND c1440 llc2160 use-case scenarios

1.	Interactive visualization of horizontal slices: In this use-case scenario, domain experts interactively explore cross-sections of DYAMOND data at different heights/depths (what we call “horizontal slices”) over time.

walkthrough of scenario:
- a domain expert selects an MITgcm or GEOS field of interest, e.g. from a dropdown list.
- given an initial overview visualization showing the entire spatial domain at a default depth, the domain expert:
-- navigates to a spatial region of interest, via pan, zoom.
-- navigates to a depth/height of interest, e.g. via a dropdown list
-- navigates to a timestep or time period of interest.
-- steps through timesteps manually (forward and backward) or animates a timeseries (loop).
-- saves the result as an mp4.

additional features:
- in addition to selecting a field of interest, the domain expert also selects a derived statistical quantity, e.g. rolling mean, to be applied to the field of interest.

2.	Interactive visualization of vertical slices: Similar to the first use-case scenario, in this scenario, domain experts interactively explore cross-sections of DYAMOND data at different latitudes or longitudes (what we call “vertical slices”) over time.

walkthrough of scenario:
- a domain expert selects either a single MITgcm/GEOS field of interest, or a coupled pair of MITgcm + GEOS fields of interest.
- the domain expert additionally indicates the location of the vertical cross-section (in degrees latitude or longitude).
- given an initial overview visualization showing the vertical slice across the entire spatial domain for the single or coupled fields, the domain expert:
-- navigates to a spatial region of interest, via pan, zoom.
-- navigates to a timestep or time period of interest.
-- steps through timesteps manually (forward and backward) or animates a timeseries (loop).
-- saves the result as an mp4.

-Note: this interface could be designed to reflect our existing vertical slicer utility, which we iteratively designed with the domain experts. In our utility, the region of interest and location of vertical slice are provided in a config file. Example animation: https://data.nas.nasa.gov/viz/vizdata/nmccurdy/DYAMOND_c1440_llc2160/dimitris/U_east-west_ocean_vel._U_eastward_wind_vel._20S-20N_140W.mp4

additional features:
-the domain expert chooses a vertical axis scaling (linear in computational levels vs. linear in physical levels (MITgcm) or pressure levels (GEOS)) – otherwise, default settings can be used, i.e. linear in computation levels for MITgcm; linear in pressure levels for GEOS.

3.	Data Extracts: In this use-case scenario, domain experts extract subsets of DYAMOND data for independent analysis.

walkthrough of scenario:
- a domain expert indicates data extract parameters:
-- MITgcm/GEOS field(s) of interest
-- (optional) derived statistical quantity (e.g. rolling mean)
-- spatial domain of interest (1D, 2D (vertical or horizontal), 3D)
-- spatial sampling (full res, downsampled)
-- temporal domain of interest (full timeseries, single timestep, time period)
-- temporal sampling
- the data extract is then exported for analysis.

4.	Space-time profiles: This use-case scenario involves generating space-time profiles of data extracts, e.g. for comparison against observations.  This is similar to data extracts, however the data for a single timestep spatial domain of interest is projected to a single value.

walkthrough of scenario:
- a domain expert space-time profile parameters:
-- MITgcm/GEOS field(s) of interest
-- (optional) derived statistical quantity (e.g. rolling mean)
-- spatial domain of interest (1D, 2D (vertical or horizontal), 3D)
-- spatial sampling (full res, downsampled)
-- temporal domain of interest (full timeseries, single timestep, time period)
-- temporal sampling
-- space-time profile function (used to project data for a single timestep to a single value – we will get example functions to work with)
- the 2D space-time profile is then exported for analysis.

# Excertps from emails
## Email 1
Because of size of model output, most users extract 3D regions, horizontal slices, or space or time subsampled fields before they carry out any analysis, rather than carry out the analysis based on the raw output files themselves.  These 3D regions or horizontal slices are then used to compute statistical quantities, in space/time or frequency/wavenumber, e.g., mean, variance, covariance, spectra, and cospectra.  One other type of application is the extraction of specific space-time profiles or time series for direct comparison with observations.

The compression approach that was used to archive the llc4320 dataset involves masking out dry cells (e.g. continents, underseabed volumes). Around half of the cells are dry, so this is a big win. Is this kind of compression something that could potentially be incorporated into your approach? Could it work with the wavelet-based spatial encoding? I'm including Bron Nelson in this email, who, along with Chris Henze, designed and implemented the compression approach along with methods to access these data.

Unfortunately for statistical quantities, we probably need to keep full available precision.  For example for computing standard deviation from mean and rms computations when the mean and rms are very similar and much larger than the  standard deviation.

Some computations need to be carried out over a full seasonal cycle, i.e., 12 months.

## Email 2
Built-in analytics are provided for the following algorithms:
1. Area-averaged time series to compute statistics (e.g., mean, minimum, maximum, standard deviation) of a single variable or two variables being compared. Optionally apply seasonal or low-pass filter to the result.
2. Time-averaged map to produce a geospatial map that averages gridded measurements over time at each grid coordinate within a user-defined spatiotemporal bounding box.
3. Correlation map to compute the correlation coefficient at each grid coordinate within a user-specified spatiotemporal bounding box for two identically gridded datasets.
4. Climatological map to compute a monthly climatology for a user-specified month and year range.
5. Daily difference average to subtract a dataset from its climatology, then, for each timestamp, average the pixel-by-pixel differences within a user-specified spatiotemporal bounding box.
6. In situ match to discover in situ measurements that correspond to a gridded satellite measurement.

From <https://www.frontiersin.org/articles/10.3389/fmars.2019.00354/full>

## Email 3
- It sounded like Dimitris and Chris were especially interested in using your framework to support exploring output from their latest GEOS-MITgcm coupled atmosphere-ocean simulation, which they *just* finished running as part of the DYAMOND (DYnamics of the Atmospheric general circulation Modeled On Non-hydrostatic Domains) initiative. The simulation is integrated using a 1440x1440 cubed sphere configuration of GEOS and a 2160x2160 lat-lon cap (2160llc) configuration of MITgcm. I will look into getting a sample of these data to experiment with, however the 4320llc dataset should still be helpful in terms of getting acquainted with MITgcm output.
- In terms of an initial project, I think we homed in on the goal of being able to interactively explore regions of the ~3.5 dimensional data (2d slices at 142 depths) both spatially -- horizontally at different depths and vertically along cross-sections of the depths --- and in time (I think Chris Hill mentioned that a week of data, with data stored either every 1hr or 15mins, would afford some really interesting exploration). Does this sound like a strong initial project? I’d be happy to discuss the idea further if it would be useful.

## Email 4
I’m attaching the example output image from the vertical slicer code. Here’s also a link to the animation:
https://data.nas.nasa.gov/viz/vizdata/nmccurdy/DYAMOND_c1440_llc2160/dimitris/U_east-west_ocean_vel._U_eastward_wind_vel._20S-20N_140W.mp4

A quick tour for reference: the top-left panel provides global view for context (here showing east-west ocean velocity). The global view shows the "region of interest" outlined in black and the vertical slice within the region of interest denoted with a bright green line. The top-middle panel shows a horizontal slice of ocean (east-west velocity) at level 0; the top-right panel shows a horizontal slice of atmosphere (eastward wind velocity) at level 0. Bright green lines indicate location of the vertical slice.
The bottom panel shows the vertical slice, with atmosphere data on top, ocean data on bottom. Bright green indicators along the right edge indicate height/depth of the horizontal atmosphere/ocean slices shown in the top-right and top-middle panels.

## Email 5
I’ve posted the vertical slicer (c++) code to the following directory:

/nobackupp1/nmccurdy/collab/pascucci/verticalSlicer

This is the code used to generate animations like the following:
https://data.nas.nasa.gov/viz/vizdata/nmccurdy/DYAMOND_c1440_llc2160/dimitris/U_east-west_ocean_vel._U_eastward_wind_vel._20S-20N_140W.mp4

If you’d like to start looking through it to see how we can go about incorporating the framework, vs.cxx draws the interface and localcut.cxx generates the slice of data.
We’ll likely build more interfaces using this kind of setup, so it would be great to figure out how to call the framework from it. We also have versions that employ zmq to distribute slicing across nodes.
