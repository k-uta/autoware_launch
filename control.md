# control config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## __diff_demo.param.yaml

**✨ Added**

```diff
--- a/config/control/__diff_demo.param.yaml
+++ b/config_lv2/control/__diff_demo.param.yaml
@@ -0,0 +1,3 @@
+/**:
+  ros__parameters:
+    test_param: true
```

## operation_mode_transition_manager/operation_mode_transition_manager.param.yaml

**✏️ Modified**

```diff
--- a/config/control/operation_mode_transition_manager/operation_mode_transition_manager.param.yaml
+++ b/config_lv2/control/operation_mode_transition_manager/operation_mode_transition_manager.param.yaml
@@ -25,3 +25,4 @@
       speed_upper_threshold: 2.0
       speed_lower_threshold: -2.0
       yaw_threshold: 0.262
+    # config-diff demo: tuned for lv2
```
