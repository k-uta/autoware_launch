# planning config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## scenario_planning/common/common.param.yaml

**✏️ Modified**

```diff
--- a/config/planning/scenario_planning/common/common.param.yaml
+++ b/config_lv2/planning/scenario_planning/common/common.param.yaml
@@ -1,6 +1,6 @@
 /**:
   ros__parameters:
-    max_vel: 4.17           # max velocity limit [m/s]
+    max_vel: 1.23  # config-diff test
 
     # constraints param for normal driving
     normal:
```
