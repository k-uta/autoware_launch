# 🔍 Config diff portal

`config` (baseline, `a`) → `config_lv2` (target, `b`)

- generated: 2026-06-11 11:27:14 UTC
- branch: [ci/config-diff-tracker](https://github.com/k-uta/autoware_launch/tree/ci/config-diff-tracker)
- files with differences: 17

## Summary

| Component | Files with diff |
| --- | --- |
| [control](control.md) | 2 |
| [localization](localization.md) | 4 |
| [map](map.md) | 1 |
| [perception](perception.md) | 4 |
| [planning](planning.md) | 1 |
| [simulator](simulator.md) | 1 |
| [system](system.md) | 3 |
| [vehicle](vehicle.md) | 1 |

## control

| Operation | File |
| --- | --- |
| ✨ Added | [`__diff_demo.param.yaml`](control.md#__diff_demoparamyaml) |
| ✏️ Modified | [`operation_mode_transition_manager/operation_mode_transition_manager.param.yaml`](control.md#operation_mode_transition_manageroperation_mode_transition_managerparamyaml) |

## localization

| Operation | File |
| --- | --- |
| ✨ Added | [`__diff_demo.param.yaml`](localization.md#__diff_demoparamyaml) |
| ✏️ Modified | [`ekf_localizer.param.yaml`](localization.md#ekf_localizerparamyaml) |
| 🗑️ Deleted | [`localization_error_monitor.param.yaml`](localization.md#localization_error_monitorparamyaml) |
| ✏️ Modified | [`twist2accel.param.yaml`](localization.md#twist2accelparamyaml) |

## map

| Operation | File |
| --- | --- |
| 🗑️ Deleted | [`map_projection_loader.param.yaml`](map.md#map_projection_loaderparamyaml) |

## perception

| Operation | File |
| --- | --- |
| ✨ Added | [`__diff_demo.param.yaml`](perception.md#__diff_demoparamyaml) |
| 🗑️ Deleted | [`occupancy_grid_map/binary_bayes_filter_updater.param.yaml`](perception.md#occupancy_grid_mapbinary_bayes_filter_updaterparamyaml) |
| ✏️ Modified | [`occupancy_grid_map/multi_lidar_pointcloud_based_occupancy_grid_map.param.yaml`](perception.md#occupancy_grid_mapmulti_lidar_pointcloud_based_occupancy_grid_mapparamyaml) |
| ✏️ Modified | [`occupancy_grid_map/pointcloud_based_occupancy_grid_map.param.yaml`](perception.md#occupancy_grid_mappointcloud_based_occupancy_grid_mapparamyaml) |

## planning

| Operation | File |
| --- | --- |
| ✏️ Modified | [`scenario_planning/common/common.param.yaml`](planning.md#scenario_planningcommoncommonparamyaml) |

## simulator

| Operation | File |
| --- | --- |
| ✏️ Modified | [`fault_injection.param.yaml`](simulator.md#fault_injectionparamyaml) |

## system

| Operation | File |
| --- | --- |
| ✨ Added | [`__diff_demo.param.yaml`](system.md#__diff_demoparamyaml) |
| ✏️ Modified | [`duplicated_node_checker/duplicated_node_checker.param.yaml`](system.md#duplicated_node_checkerduplicated_node_checkerparamyaml) |
| 🗑️ Deleted | [`pipeline_latency_monitor/pipeline_latency_monitor.param.yaml`](system.md#pipeline_latency_monitorpipeline_latency_monitorparamyaml) |

## vehicle

| Operation | File |
| --- | --- |
| ✏️ Modified | [`raw_vehicle_cmd_converter/raw_vehicle_cmd_converter.param.yaml`](vehicle.md#raw_vehicle_cmd_converterraw_vehicle_cmd_converterparamyaml) |
