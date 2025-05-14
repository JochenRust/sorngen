------------------------------------------------------
-- SORNGEN VHDL FUNCTION GENERATOR 
-- Engine: 		0.1
-- Filename: 		POW0.vhd
-- Author: 		n/a
-- Info: 		
-- SORN function
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity POW0 is
       port(
       -- input port(s)
       input0 : IN std_logic_vector(6 downto 0);
       -- output port(s)
       output0 : OUT std_logic_vector(6 downto 0)
       );
end POW0;

------------------------------------------------------
-- input 0 (input0) encoding
-- x0(0): [-inf,-2.0)
-- x0(1): [-2.0,-1.0)
-- x0(2): [-1.0,0.0)
-- x0(3): [0.0,0.0]
-- x0(4): (0.0,1.0]
-- x0(5): (1.0,2.0]
-- x0(6): (2.0,inf]

-- input 1 (input0) encoding
-- none
-- result  (output0) encoding
-- result(0): [-inf,-2.0)
-- result(1): [-2.0,-1.0)
-- result(2): [-1.0,0.0)
-- result(3): [0.0,0.0]
-- result(4): (0.0,1.0]
-- result(5): (1.0,2.0]
-- result(6): (2.0,inf]

------------------------------------------------------
architecture Behavior of POW0 is     

-- components
-- none
-- signals
signal x0 : std_logic_vector(6 downto 0);
signal result : std_logic_vector(6 downto 0);

begin

-- instantiation/function
result(0) <=  '0';
result(1) <=  '0';
result(2) <=  '0';
result(3) <= x0(3);
result(4) <= x0(2) or x0(4);
result(5) <= x0(1) or x0(5);
result(6) <= x0(0) or x0(1) or x0(5) or x0(6);


-- assignments
x0 <= input0;
output0 <= result;


end Behavior;