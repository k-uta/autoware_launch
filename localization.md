# localization config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## __diff_demo.param.yaml

**✨ Added**

```diff
--- a/config/localization/__diff_demo.param.yaml
+++ b/config_lv2/localization/__diff_demo.param.yaml
@@ -0,0 +1,3 @@
+/**:
+  ros__parameters:
+    diff_demo_localization: true
```

## ekf_localizer.param.yaml

**✏️ Modified**

```diff
--- a/config/localization/ekf_localizer.param.yaml
+++ b/config_lv2/localization/ekf_localizer.param.yaml
@@ -52,3 +52,4 @@
       # for velocity measurement limitation (Set 0.0 if you want to ignore)
       threshold_observable_velocity_mps: 0.0 # [m/s]
       pose_frame_id: "map"
+    # config-diff demo: tuned for lv2
```

## localization_error_monitor.param.yaml

**🗑️ Deleted**

```diff
--- a/config/localization/localization_error_monitor.param.yaml
+++ b/config_lv2/localization/localization_error_monitor.param.yaml
@@ -1,7 +0,0 @@
-/**:
-  ros__parameters:
-    scale: 3.0
-    error_ellipse_size: 1.5
-    warn_ellipse_size: 1.2
-    error_ellipse_size_lateral_direction: 0.3
-    warn_ellipse_size_lateral_direction: 0.25
```

## twist2accel.param.yaml

**✏️ Modified**

```diff
--- a/config/localization/twist2accel.param.yaml
+++ b/config_lv2/localization/twist2accel.param.yaml
@@ -2,3 +2,4 @@
   ros__parameters:
     use_odom: true
     accel_lowpass_gain: 0.9
+    # config-diff demo: tuned for lv2
```
