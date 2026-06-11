# vehicle config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## raw_vehicle_cmd_converter/raw_vehicle_cmd_converter.param.yaml

**✏️ Modified**

```diff
--- a/config/vehicle/raw_vehicle_cmd_converter/raw_vehicle_cmd_converter.param.yaml
+++ b/config_lv2/vehicle/raw_vehicle_cmd_converter/raw_vehicle_cmd_converter.param.yaml
@@ -31,3 +31,4 @@
     vgr_coef_b: 0.053
     vgr_coef_c: 0.042
     convert_actuation_to_steering_status: false
+    # config-diff demo: tuned for lv2
```
