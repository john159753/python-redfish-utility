## Persistent Memory Commands

This section includes commands related to the discovery and configuration of HPE Persistent Memory.

### Persistent Memory Discovery Command


> Example: Show information about the physical persistent memory modules.


<pre>
iLOrest > <font color="#01a982">showpmm --device</font>

Location        Capacity    Status    DIMMStatus    Life    FWVersion
PROC 1 DIMM 1   126.38 GB   OK        GoodInUse     100%    01.02.00.5360
PROC 1 DIMM 12  126.38 GB   OK        GoodInUse     100%    01.02.00.5360
PROC 2 DIMM 1   126.38 GB   OK        GoodInUse     100%    01.02.00.5360
PROC 2 DIMM 12  126.38 GB   OK        GoodInUse     100%    01.02.00.5360

</pre>


> Example: Show current configuration of selected persistent memory modules.


<pre>
iLOrest > <font color="#01a982">showpmm --config --dimm=1@12,2@12</font>

Location        VolatileSize    PmemSize    PmemInterleaved
PROC 1 DIMM 12  126.38 GB       0.0 GB      N/A
PROC 2 DIMM 12  126.38 GB       0.0 GB      N/A

</pre>


> Example: Show the persistent interleave regions in JSON format.


<pre>
iLOrest > <font color="#01a982">showpmm --logical --dimm=1@12,2@12</font>

[ { 'DimmIds': '1@1, 1@12',
    'PmemSize': { 'Units': 'GB',
                  'Value': 252.0}},
  { 'DimmIds': '2@1, 2@12',
    'PmemSize': { 'Units': 'GB',
                  'Value': 252.0}}]

</pre>


> Example: Show a summary of the persistent memory resources.


<pre>
iLOrest > <font color="#01a982">showpmm --summary</font>

TotalCapacity:  505.52 GB
TotalVolatileSize:  505.52 GB
TotalPmemSize:  0.0 GB

</pre>


#### Syntax


showpmm --device | -D [--dimm=(DIMM IDs) | -I] [--json | -j]

showpmm --config | -C [--dimm=(DIMM IDs) | -I] [--json | -j]

showpmm --logical | -L [--json | -j]

showpmm --summary | -M [--json | -j]


#### Description


Displays information about the installed persistent memory modules.


#### Parameters


- **-h, --help**

Displays help on the usage of this command.

- **-D, --device**

Shows a physical overview of the installed persistent memory modules.

- **-C, --config**

Shows the current configuration of the installed persistent memory modules.

- **-L, --logical**

Shows the persistent interleave sets (if present).

- **-M, --summary**

Shows a summary of the installed persistent memory modules.

- **-I, --dimm**

Optionally, use this flag to filter output by DIMM IDs (ProcessorNumber@SlotNumber). Can be used in conjunction with the `-D | --device` or the `-C | --config` flags.

- **-j, --json**

Optionally use this flag to display output in JSON format.


### Persistent Memory Guided Configuration Command


> Example: Show a list of supported guided configurations.


<pre>
iLOrest > <font color="#01a982">applypmmconfig --list</font>

Available Configurations:

MemoryMode
        Configure all PMMs to 100% Memory Mode.
PmemInterleaved
        Configure all PMMs to 100% Persistent. Interleave the Persistent memory regions within each processor.
PmemNotInterleaved
        Configure all PMMs to 100% Persistent. The Persistent memory regions are not interleaved.

</pre>


> Example: Configure all installed persistent memory modules as 100% Volatile.


<pre>
iLOrest > <font color="#01a982">applypmmconfig --config MemoryMode</font>


***WARNING: Configuration changes require reboot to take effect***

Operation    PmemSize    VolatileSize    DimmIds
CREATE       0.0 GB      252.76 GB       1@1, 1@12
CREATE       0.0 GB      252.76 GB       2@1, 2@12

</pre>


#### Syntax


applypmmconfig -L | --list

applypmmconfig -C | --config [-f | --force]


#### Description


Apply a pre-defined configuration to the installed persistent memory modules.


#### Parameters


- **-h, --help**

Displays help on the usage of this command.

- **-L, --list**

Display a list of available pre-defined configIDs along with a brief description.

- **-C, --config**

Specify one of the pre-defined configIDs to apply to all the persistent memory modules.

- **-f, --force**

Allow the user to force the configuration by automatically accepting any prompts.


### Persistent Memory Advanced Configuration Command


> Example: Configure all persistent memory modules on processors 1 and 3 to 50% Volatile with no persistent interleave regions.


<pre>
iLOrest > <font color="#01a982">provisionpmm -m 50 -i off -p 1,3</font>

***WARNING: Configuration changes require reboot to take effect***

Operation    PmemSize    VolatileSize    DimmIds
CREATE       63.19 GB    63.19 GB        1@1
CREATE       63.19 GB    63.19 GB        1@12
CREATE       63.19 GB    63.19 GB        3@1
CREATE       63.19 GB    63.19 GB        3@12

</pre>


> Example: Configure all installed persistent memory modules to 25% Volatile with persistent interleave regions.


<pre>
iLOrest > <font color="#01a982">provisionpmm -m 25 -i on</font>

***WARNING: Configuration changes require reboot to take effect***

Operation    PmemSize    VolatileSize    DimmIds
DELETE       126.0 GB    126.76 GB       1@1, 1@12
DELETE       126.0 GB    126.76 GB       2@1, 2@12
CREATE       189.57 GB   63.19 GB        1@1, 1@12
CREATE       189.57 GB   63.19 GB        2@1, 2@12

</pre>


#### Syntax


provisionpmm [-h | --help] [-m | --memory-mode=(0|%)] [-i | --pmem-interleave=(On|Off)] [-p | --proc=(processorID)] [-f | --force]


#### Description


Applies user specified configuration to the persistent memory modules.


#### Parameters


- **-h, --help**

Displays help on the usage of this command.

- **-m, --memory-mode**

Optionally allows user to specify the percentage of total capacity that should be configured as Volatile. Defaults to 0% Volatile. The remaining capacity will be configured as Persistent.

- **-i, --pmem-interleave**

Indicates whether the persistent memory regions should be interleaved (Allowed values: "on", "off").

- **-p, --proc**

Optionally allows user to specify the processors (comma separated list of ProcessorNumbers) on which the selected configuration would be applied. Defaults to all processors.

- **-f, --force**

Allows the user to force the configuration by automatically accepting any prompts.


### Show Pending Configuration Command


> Example: Show persistent memory configuration changes pending a reboot.


<pre>
iLOrest > <font color="#01a982">showpmmpendingconfig</font>

Operation    PmemSize    VolatileSize    DimmIds
DELETE       190.0 GB    62.76 GB        1@1, 1@12
DELETE       190.0 GB    62.76 GB        2@1, 2@12
CREATE       94.78 GB    31.59 GB        1@1
CREATE       94.78 GB    31.59 GB        1@12
CREATE       94.78 GB    31.59 GB        2@1
CREATE       94.78 GB    31.59 GB        2@12

</pre>


#### Syntax


showpmmpendingconfig [-j | --json]


#### Description


Shows the queued tasks pending a reboot for configuring the persistent memory modules.


#### Parameters


- **-h, --help**

Displays help on the usage of this command.

- **-j, --json**

Optionally, use this flag to display output in JSON format.


### Clear Pending Configuration Command


> Example: Clears all the pending persistent memory configuration tasks.


<pre>
iLOrest > <font color="#01a982">clearpmmpendingconfig</font>

Deleted Task #1948
Deleted Task #1949
Deleted Task #1950
Deleted Task #1951
Deleted Task #1952
Deleted Task #1953

</pre>


#### Syntax


clearpmmpendingconfig


#### Description


Clears all the pending persistent memory configuration tasks.

#### Parameters


- **-h, --help**

Displays help on the usage of this command.


### Show Recommended Configuration Command


> Example: Show a list of recommended persistent memory configurations


<pre>
iLOrest > <font color="#01a982">showrecommendedpmmconfig</font>

MemoryModeTotalSize    PmemTotalSize    CacheRatio
0 GB                   505 GB           N/A
377 GB                 128 GB           1:2.9
505 GB                 0 GB             1:3.9

</pre>

#### Syntax


showrecommendedpmmconfig


#### Description


Shows the recommended persistent memory configurations.


#### Parameters


- **-h, --help**

Displays help on the usage of this command.