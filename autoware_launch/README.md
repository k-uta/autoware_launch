# autoware_launch

## Structure

![autoware_launch](./autoware_launch.drawio.svg)

## Package Dependencies

Please see `<exec_depend>` in `package.xml`.

## Usage

You can use the command as follows at shell script to launch `*.launch.xml` in `launch` directory.

```bash
ros2 launch autoware_launch autoware.launch.xml map_path:=/path/to/map_folder vehicle_model:=lexus sensor_model:=aip_xx1
```

## Autonomy level (lv2 / lv4)

The installed share directory points at one autonomy level at a time. Switch it while Autoware is
stopped; switching a running system is not supported.

```bash
ros2 run autoware_launch show_autonomy_level.sh     # prints lv2 or lv4
ros2 run autoware_launch switch_autonomy_level.sh lv2
```

The choice survives `colcon build`. `show_autonomy_level.sh` exits 1 without printing a level if the
`config` symlink, the symlinks under `launch/` and `share/autoware_launch/current_level.txt`
disagree.

Level differences go into `config_lv2/` and `launch_lv2/`; `config/` and `launch/` stay as the lv4
trees that upstream changes land in.

`config` is installed as a directory symlink, but `launch/` is a real directory of per-file symlinks
into `share/autoware_launch_levels/launch_<level>`. This is forced by `ros2launch`, which walks the
share directory with `os.walk`: it does not follow directory symlinks and fails when a launch file
name matches more than once.
