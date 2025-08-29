# Adjusting atmosphere restarts for new land cover maps

Changes are commonly made to the land cover maps in the coupled model e.g. accounting for new historical land use change datasets, addition of new tiles to the model. The way the atmosphere-land model currently behaves makes the generation of initial conditions for these experiments difficult. The land model only populates the active tiles with meaningful physical values for the tiled variables e.g. soil moisture and temperature, nutrient pools. The inactive tiles remain 0.0. When a new tile becomes active due to a change in the land cover map, and a condition from a previous run is used a starting condition (restart), the new tiles pick up non-sensical values for these quantities and typically cause the model to fail.

This tool fills adjusts a given restart to give the newly active tiles reasonable values, so that the model does not crash on startup and can eventually equilibriate.

## The scientific process

Choosing a value for the new tile is not always a trivial task. There are two "classes" of variables:

1. Tile agnostic variables, which are not strongly tied to the classification of the tile. These are variables like soil moisture and temperature, snow.
2. Tile specific variables, which are strongly tied to the classification of the tile. These are variables like the nutrient pools, LAI.

A separate technique is used to fill tiles for these two classes.

### Tile agnostic variables

The process is simple for tile agnostic variables. We make the assumption that the land mask will not change, which means that for any newly active tile, there will always be other tiles on that grid cell with physically reasonable values to use as a basis for the new tile. Currently, a area-fraction weighted average from the previously active tiles on the grid cell is applied to any new tiles on the grid cell.

For example, if a C4 grass tile is added to a grid cell that was previously 75% evergreen broadleaf and 25% C3 grass, with the soil temperature on the those being 300.0K and 302.0K respectively, the soil temperature on the new C4 tile would be `0.75 * 300.0 + 0.25 * 302.0K = 300.5K`.

### Tile specific variables

The process is more complicated for tile specific variables. Only tiles from the same or similar classifications can be used as "reference" data for these new tiles. Using the nutrient pools from an existing deciduous broadleaf type and shrub tiles to fill a new C3 grass tile would likely cause significant physical issues, as they respond very differently to amounts and nutrient ratios. Thus, the first step is to determine which tile classifications are valid candidates to use as source data for other tiles.

By default, this is strictly a self-to-self relationship- a given tile classification can only use itself as source data e.g. evergreen broadleaf can only source its nutrient data from existing evergreen broadleaf tiles. The tool can be configured to add candidates for a tile e.g. evergreen broadleaf can source its nutrient data from evergreen broadleaf and evergreen needleleaf.

Once candidates for each tile are determined, we can search for previously active tiles to fill in the new tiles. The search continues until a minimum number of valid source tiles are found, with the default minimum being 1. The search consists of 4 stages:

1. Search for valid tiles on the same grid cell as the new tile.
2. Search for valid tiles on a specified square around the cell. The square size is specified in the configuration, in terms of number of cells.
3. Search for valid tiles in a latitude band around the cell. The size of the band is specified in the configuration, in terms in the number of cells.
3. Search globally for valid tiles.

Once the search is complete, the specific variable in the new tile is set to the non-weighted average of the valid tiles found in the search. If no valid tiles are found anywhere i.e. a completely new tile classification is introduced and a different source classification was not set up, then the value is set to 0.0.
