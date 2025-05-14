------------------------------------------------------
-- SORNGEN VHDL FUNCTION GENERATOR 
-- Engine: 		0.1
-- Filename: 		z1_module.vhd
-- Author: 		n/a
-- Info: 		
-- SORNGEN TOPLEVEL
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity z1_module is
       port(
       -- input port(s)
       x : IN std_logic_vector(6 downto 0);
       -- output port(s)
       z1 : OUT std_logic_vector(6 downto 0)
       );
end z1_module;

architecture Behavior of z1_module is     

-- components
component POW0
       port(
       -- input port(s)
       input0 : IN std_logic_vector(6 downto 0);
       -- output port(s)
       output0 : OUT std_logic_vector(6 downto 0)
       );
end component;


-- signals
signal POW0_to_z1 : std_logic_vector(6 downto 0);
signal x_to_POW0 : std_logic_vector(6 downto 0);

begin

-- instantiation/function
i_POW0 : POW0 port map(
       input0 => x_to_POW0,
output0 => POW0_to_z1
       );



-- assignments
z1 <= POW0_to_z1;
x_to_POW0 <= x;


end Behavior;