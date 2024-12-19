function modbus_read(block)
  setup(block); % Setup function to initialize block properties
  
  % Start method to establish Modbus TCP connection
  function Start(block)
    % Get IP address and port number from dialog parameters
    address = block.DialogPrm(2).Data;
    port = block.DialogPrm(3).Data;
    
    % Open Modbus TCP connection
    ModBusTCP = openConnection(address, port);
    
    % Store connection in block handle for future use
    set_param(block.BlockHandle, 'UserData', ModBusTCP);
  end
  
  % Outputs method to handle output data
  function Outputs(block)
    % Output the data from Dwork
    block.OutputPort(1).Data = block.Dwork(1).Data;
  end
  
  % Update method to read data from Modbus server
  function Update(block)
    % Retrieve the Modbus TCP connection
    ModBusTCP = get_param(block.BlockHandle, 'UserData');
    
    % Get the Modbus register address from the dialog parameters
    registry = block.DialogPrm(1).Data;
    
    % Define the Modbus target (register type)
    target = 'holdingregs';  % Set this to the correct target (e.g., 'coils', 'inputregs', etc.)
    
    % Read floating-point data from the Modbus server
    response = readFloating(ModBusTCP, target, registry);
    
    % Store the result in Dwork (used as a state for the block)
    block.Dwork(1).Data = double(response);
  end

  % Setup function to configure input/output ports and block properties
  function setup(block)
    block.NumInputPorts  = 0;  % No input ports
    block.NumOutputPorts = 1;  % One output port
    block.SetPreCompPortInfoToDefaults;
    
    block.OutputPort(1).DatatypeID  = 0;  % Data type (double)
    block.OutputPort(1).Complexity  = 'Real';  % Real values (no complex numbers)
    
    block.NumDialogPrms     = 3;  % Number of dialog parameters (e.g., address, port, registry)
    block.DialogPrmsTunable = {'Nontunable', 'Nontunable', 'Nontunable'};
    
    block.SampleTimes = [0.1 0];  % Set explicit sample time (e.g., 0.1 seconds)
    
    block.SetAccelRunOnTLC(false);  % Disable accelerated simulation on TLC
    block.RegBlockMethod('SetInputPortDimensions', @SetInpPortDims);
    block.RegBlockMethod('SetInputPortDataType', @SetInpPortDataType);
    block.RegBlockMethod('SetOutputPortDimensions', @SetOutPortDims);
    block.RegBlockMethod('SetOutputPortDataType', @SetOutPortDataType);
    block.RegBlockMethod('PostPropagationSetup', @DoPostPropSetup);
    block.RegBlockMethod('ProcessParameters', @ProcessPrms);
    block.RegBlockMethod('Start', @Start);
    block.RegBlockMethod('Outputs', @Outputs);
    block.RegBlockMethod('Update', @Update);
  end

  % Process runtime parameters
  function ProcessPrms(block)
    block.AutoUpdateRuntimePrms;
  end

  % Set input port dimensions (if any)
  function SetInpPortDims(block, idx, di)
    block.InputPort(idx).Dimensions = di;
    block.OutputPort(1).Dimensions  = di;
  end
  
  % Set input port data type (if any)
  function SetInpPortDataType(block, idx, dt)
    block.InputPort(idx).DataTypeID = dt;
    block.OutputPort(1).DataTypeID  = dt;
  end

  % Set output port dimensions
  function SetOutPortDims(block, idx, di)
    block.OutputPort(idx).Dimensions = di;
    block.InputPort(1).Dimensions    = di;
  end

  % Set output port data type
  function SetOutPortDataType(block, idx, dt)
    block.OutputPort(idx).DataTypeID  = dt;
    block.InputPort(1).DataTypeID     = dt;
  end

  % Post-propagation setup (Dwork initialization)
  function DoPostPropSetup(block)
    block.NumDworks = 1;  % Number of Dwork variables
    block.Dwork(1).Name            = 'result';
    block.Dwork(1).Dimensions      = 1;  % Single value (assuming one register)
    block.Dwork(1).DatatypeID      = 0;  % double
    block.Dwork(1).Complexity      = 'Real';  % Real values
    block.Dwork(1).UsedAsDiscState = true;
    block.AutoRegRuntimePrms;
  end

  % Open Modbus TCP connection
  function ModBusTCP = openConnection(ipaddress, port)
    ModBusTCP = modbus('tcpip', ipaddress, port);
    ModBusTCP.ByteOrder = 'big-endian';  % Set byte order
  end

  % Read floating-point data from Modbus server
  function response = readFloating(ModBusTCP, target, registry)
    response = read(ModBusTCP, target, registry, 1, 'single');  % Read 1 register as 'single' (float)
  end
end
