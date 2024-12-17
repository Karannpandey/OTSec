function modbus_read(block)
setup(block);

function Start(block)
    address = block.DialogPrm(2).Data;
    port = block.DialogPrm(3).Data;
    try
        ModBusTCP = openConnection(address, port);
        set_param(block.BlockHandle, 'UserData', ModBusTCP);
    catch ME
        error(['Connection Error: ', ME.message]);
    end

function Outputs(block)
    block.OutputPort(1).Data = block.Dwork(1).Data;

function Update(block)
    ModBusTCP = get_param(block.BlockHandle, 'UserData');
    registry = block.DialogPrm(1).Data;
    target = 'holdingregs';
    try
        response = readFloating(ModBusTCP, target, registry);
        block.Dwork(1).Data = double(response);
    catch ME
        warning(['Read Error: ', ME.message]);
        block.Dwork(1).Data = NaN;
    end

function Terminate(block)
    ModBusTCP = get_param(block.BlockHandle, 'UserData');
    if ~isempty(ModBusTCP)
        close(ModBusTCP);
    end

function setup(block)
    block.NumInputPorts  = 0;
    block.NumOutputPorts = 1;
    block.SetPreCompPortInfoToDefaults;
    block.OutputPort(1).DatatypeID  = 0; % double
    block.OutputPort(1).Complexity  = 'Real';
    block.NumDialogPrms     = 3;
    block.DialogPrmsTunable = {'Nontunable','Nontunable','Nontunable'};
    block.SampleTimes = [-1 0];
    block.SetAccelRunOnTLC(false);
    block.RegBlockMethod('Start', @Start);
    block.RegBlockMethod('Outputs', @Outputs);
    block.RegBlockMethod('Update', @Update);
    block.RegBlockMethod('Terminate', @Terminate);
    block.RegBlockMethod('PostPropagationSetup', @DoPostPropSetup);

function ModBusTCP = openConnection(ipaddress, port)
    ModBusTCP = modbus('tcpip', ipaddress, port);
    ModBusTCP.ByteOrder = 'big-endian';

function response = readFloating(ModBusTCP, target, registry)
    response = read(ModBusTCP, target, registry, 1, 'single');
