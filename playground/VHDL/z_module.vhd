------------------------------------------------------
-- SORNGEN VHDL FUNCTION GENERATOR 
-- Engine: 		0.1
-- Filename: 		z_module.vhd
-- Author: 		n/a
-- Info: 		
-- SORNGEN TOPLEVEL
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity z_module is
       port(
       -- input port(s)
       z1 : IN std_logic_vector(6 downto 0);
y : IN std_logic_vector(6 downto 0);
       -- output port(s)
       z : OUT std_logic_vector(6 downto 0)
       );
end z_module;

architecture Behavior of z_module is     

-- components
component ADD0
       port(
       -- input port(s)
       input0 : IN std_logic_vector(6 downto 0);
input1 : IN std_logic_vector(6 downto 0);
       -- output port(s)
       output0 : OUT std_logic_vector(6 downto 0)
       );
end component;


-- signals
signal ADD0_to_z : std_logic_vector(6 downto 0);
signal z1_to_ADD0 : std_logic_vector(6 downto 0);
signal y_to_ADD0 : std_logic_vector(6 downto 0);

begin

-- instantiation/function
i_ADD0 : ADD0 port map(
       input0 => z1_to_ADD0,
input1 => y_to_ADD0,
output0 => ADD0_to_z
       );



-- assignments
z <= ADD0_to_z;
z1_to_ADD0 <= z1;
y_to_ADD0 <= y;


end Behavior;