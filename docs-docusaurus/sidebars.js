/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    'index',
    'Overview',
    'Features',
    'FAQ',
    'Config_Changes',
    {
      type: 'category',
      label: 'Configuration',
      link: {
        type: 'generated-index',
        title: 'Configuration',
      },
      items: [
        'Config_Reference',
        'Kalico_Additions',
        {
          type: 'category',
          label: 'Bleeding Edge',
          items: [
            'Bleeding_Edge',
            'Config_Reference_Bleeding_Edge',
            'Nonlinear_Pressure_Advance',
          ],
        },
        'PID',
        'MPC',
        'Dockable_Probe',
      ],
    },
    {
      type: 'category',
      label: 'G-Code Reference',
      link: {
        type: 'generated-index',
        title: 'G-Code Reference',
      },
      items: [
        'G-Codes',
        'Command_Templates',
        'G-Code_Shell_Command',
        'Status_Reference',
      ],
    },
    {
      type: 'category',
      label: 'Getting up and running',
      link: {
        type: 'generated-index',
        title: 'Getting up and running',
      },
      items: [
        'Migrating_from_Klipper',
        'Installation',
        'OctoPrint',
        'TMC_Drivers',
        'Config_checks',
        'Rotation_Distance',
        'Multi_MCU_Homing',
        {
          type: 'category',
          label: 'Bed leveling, Probes and Endstops',
          items: [
            'Z_Calibration',
            'Bed_Level',
            'Delta_Calibrate',
            'Probe_Calibrate',
            'BLTouch',
            'Manual_Level',
            'Bed_Mesh',
            'Endstop_Phase',
            'Axis_Twist_Compensation',
            'Skew_Correction',
          ],
        },
        {
          type: 'category',
          label: 'Tuning',
          items: [
            'Measuring_Resonances',
            'Resonance_Compensation',
            'Pressure_Advance',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Slicers',
      link: {
        type: 'generated-index',
        title: 'Slicers',
      },
      items: [
        'Slicers',
        'Exclude_Object',
        'Using_PWM_Tools',
      ],
    },
    {
      type: 'category',
      label: 'Developer Documentation',
      link: {
        type: 'generated-index',
        title: 'Developer Documentation',
      },
      items: [
        'Code_Overview',
        'Kinematics',
        'Protocol',
        'API_Server',
        'MCU_Commands',
        'CANBUS_protocol',
        'Debugging',
        'Benchmarks',
        'CONTRIBUTING',
        'Packaging',
      ],
    },
    {
      type: 'category',
      label: 'Device Specific Documents',
      link: {
        type: 'generated-index',
        title: 'Device Specific Documents',
      },
      items: [
        'Example_Configs',
        'SDCard_Updates',
        'RPi_microcontroller',
        'Beaglebone',
        'Bootloaders',
        'Bootloader_Entry',
        'CANBUS',
        'CANBUS_Troubleshooting',
        'TSL1401CL_Filament_Width_Sensor',
        'Hall_Filament_Width_Sensor',
        'Load_Cell',
      ],
    },
    'Telemetry',
    'Contact',
    'Sponsors',
  ],
};

module.exports = sidebars;
