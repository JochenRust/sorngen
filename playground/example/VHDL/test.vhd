------------------------------------------------------
-- SORNGEN VHDL FUNCTION GENERATOR 
-- Engine: 		0.1
-- Filename: 		test.vhd
-- Author: 		n/a
-- Info: 		
-- SORNGEN TOPLEVEL
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity test is
       port(
       -- input port(s)
       x : IN std_logic_vector(6 downto 0);
y : IN std_logic_vector(6 downto 0);
       -- output port(s)
       z1 : OUT std_logic_vector(6 downto 0);
z : OUT std_logic_vector(6 downto 0)
       );
end test;

architecture Behavior of test is     

-- components
component z1_module
       port(
       -- input port(s)
       x : IN std_logic_vector(6 downto 0);
       -- output port(s)
       z1 : OUT std_logic_vector(6 downto 0)
       );
end component;

component z_module
       port(
       -- input port(s)
       z1 : IN std_logic_vector(6 downto 0);
y : IN std_logic_vector(6 downto 0);
       -- output port(s)
       z : OUT std_logic_vector(6 downto 0)
       );
end component;


-- signals
signal z1_module_to_z1 : std_logic_vector(6 downto 0);

begin

-- instantiation/function
i_z1_module : z1_module port map(
       z1 => z1_module_to_z1,
x => x
       );

i_z_module : z_module port map(
       z => z,
z1 => z1_module_to_z1,
y => y
       );



-- assignments
z1 <= z1_module_to_z1;


end Behavior;