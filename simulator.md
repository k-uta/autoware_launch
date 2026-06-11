# simulator config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## fault_injection.param.yaml

**✏️ Modified**

```diff
--- a/config/simulator/fault_injection.param.yaml
+++ b/config_lv2/simulator/fault_injection.param.yaml
@@ -35,3 +35,4 @@
       /sensing/gnss/node_alive_monitoring: "gnss_connection"
       /system/node_alive_monitoring: "system_topic_status"
       /vehicle/node_alive_monitoring: "vehicle_topic_status"
+    # config-diff demo: tuned for lv2
```
