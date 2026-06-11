# system config diff

`config` (a) → `config_lv2` (b) · [← portal](README.md)

## __diff_demo.param.yaml

**✨ Added**

```diff
--- a/config/system/__diff_demo.param.yaml
+++ b/config_lv2/system/__diff_demo.param.yaml
@@ -0,0 +1,3 @@
+/**:
+  ros__parameters:
+    diff_demo_system: true
```

## duplicated_node_checker/duplicated_node_checker.param.yaml

**✏️ Modified**

```diff
--- a/config/system/duplicated_node_checker/duplicated_node_checker.param.yaml
+++ b/config_lv2/system/duplicated_node_checker/duplicated_node_checker.param.yaml
@@ -5,3 +5,4 @@
     nodes_to_ignore:  # List of nodes to ignore when checking for duplicates
       - /rviz2
       - /simulation/getParameter
+    # config-diff demo: tuned for lv2
```

## pipeline_latency_monitor/pipeline_latency_monitor.param.yaml

**🗑️ Deleted**

```diff
--- a/config/system/pipeline_latency_monitor/pipeline_latency_monitor.param.yaml
+++ b/config_lv2/system/pipeline_latency_monitor/pipeline_latency_monitor.param.yaml
@@ -1,57 +0,0 @@
-/**:
-  ros__parameters:
-    update_rate: 10.0
-    latency_threshold_ms: 1000.0
-    window_size: 10
-
-    processing_steps:  # processing steps used to calculate the latency.
-      # The name of the steps are only used for setting the parameters and for debug outputs
-      sequence:  # sequence ordered from first to last step
-        - multi_object_tracker
-        - decorative_object_merger_node
-        - map_based_prediction
-        - planning
-        - control
-      # Each step needs to be associated with a topic, a topic type, a timestamp meaning, and a multiplier
-      multi_object_tracker:
-        topic: # input topic with the timestamp and the latency duration of the processing step
-          /perception/object_recognition/tracking/multi_object_tracker/debug/meas_to_tracked_object_ms
-        topic_type: # type of the input topic
-          autoware_internal_debug_msgs/msg/Float64Stamped
-        timestamp_meaning: "end" # whether the timestamp represent the "start" or "end" time of the step
-        latency_multiplier: 1.0 # multiplier to convert the input latency duration into ms (e.g., 1e3 for s->ms, 1e-3 for us->ms)
-      decorative_object_merger_node:
-        topic: # input topic with the timestamp and the latency duration of the processing step
-          /perception/object_recognition/tracking/decorative_object_merger_node/debug/processing_time_ms
-        topic_type: # type of the input topic
-          autoware_internal_debug_msgs/msg/Float64Stamped
-        timestamp_meaning: "end" # whether the timestamp represent the "start" or "end" time of the step
-        latency_multiplier: 1.0 # multiplier to convert the input latency duration into ms (e.g., 1e3 for s->ms, 1e-3 for us->ms)
-      map_based_prediction:
-        topic: # input topic with the timestamp and the latency duration of the processing step
-          /perception/object_recognition/prediction/map_based_prediction/debug/processing_time_ms
-        topic_type: # type of the input topic
-          autoware_internal_debug_msgs/msg/Float64Stamped
-        timestamp_meaning: "end" # whether the timestamp represent the "start" or "end" time of the step
-        latency_multiplier: 1.0  # multiplier to convert the input latency duration into ms (e.g., 1e3 for s->ms, 1e-3 for us->ms)
-      planning:
-        topic: # input topic with the timestamp and the latency duration of the processing step
-          /planning/planning_validator/validation_status
-        topic_type: # type of the input topic
-          autoware_planning_validator/msg/PlanningValidatorStatus
-        timestamp_meaning: "end" # whether the timestamp represent the "start" or "end" time of the step
-        latency_multiplier: 1.0e3 # multiplier to convert the input latency duration into ms (e.g., 1e3 for s->ms, 1e-3 for us->ms)
-      control:
-        topic: # input topic with the timestamp and the latency duration of the processing step
-          /control/control_component_latency
-        topic_type: # type of the input topic
-          autoware_internal_debug_msgs/msg/Float64Stamped
-        timestamp_meaning: "end" # whether the timestamp represent the "start" or "end" time of the step
-        latency_multiplier: 1.0e3 # multiplier to convert the input latency duration into ms (e.g., 1e3 for s->ms, 1e-3 for us->ms)
-
-    latency_offsets_ms:  # [ms] extra offset to add to the total latency
-      - 0.0 # sensing
-      - 1.4 # perception
-      - 50.0 # planning
-      - 15.0 # control
-      - 191.0 # vehicle interface
```
