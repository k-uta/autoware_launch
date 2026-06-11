# perception config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## __diff_demo.param.yaml

**✨ Added**

```diff
--- a/config/perception/__diff_demo.param.yaml
+++ b/config_lv2/perception/__diff_demo.param.yaml
@@ -0,0 +1,3 @@
+/**:
+  ros__parameters:
+    diff_demo_perception: true
```

## occupancy_grid_map/binary_bayes_filter_updater.param.yaml

**🗑️ Deleted**

```diff
--- a/config/perception/occupancy_grid_map/binary_bayes_filter_updater.param.yaml
+++ b/config_lv2/perception/occupancy_grid_map/binary_bayes_filter_updater.param.yaml
@@ -1,8 +0,0 @@
-/**:
-  ros__parameters:
-    probability_matrix:
-      occupied_to_occupied: 0.95
-      occupied_to_free: 0.05
-      free_to_occupied: 0.2
-      free_to_free: 0.8
-    v_ratio: 10.0
```

## occupancy_grid_map/multi_lidar_pointcloud_based_occupancy_grid_map.param.yaml

**✏️ Modified**

```diff
--- a/config/perception/occupancy_grid_map/multi_lidar_pointcloud_based_occupancy_grid_map.param.yaml
+++ b/config_lv2/perception/occupancy_grid_map/multi_lidar_pointcloud_based_occupancy_grid_map.param.yaml
@@ -60,3 +60,4 @@
       # Setting2: tune ogm fusion parameters
       ## choose fusion method from ["overwrite", "log-odds", "dempster-shafer"]
         fusion_method: "overwrite"
+    # config-diff demo: tuned for lv2
```

## occupancy_grid_map/pointcloud_based_occupancy_grid_map.param.yaml

**✏️ Modified**

```diff
--- a/config/perception/occupancy_grid_map/pointcloud_based_occupancy_grid_map.param.yaml
+++ b/config_lv2/perception/occupancy_grid_map/pointcloud_based_occupancy_grid_map.param.yaml
@@ -37,3 +37,4 @@
     publish_processing_time_detail: false
     processing_time_tolerance_ms: 50.0 # [ms]
     processing_time_consecutive_excess_tolerance_ms: 1000.0 # [ms]
+    # config-diff demo: tuned for lv2
```
