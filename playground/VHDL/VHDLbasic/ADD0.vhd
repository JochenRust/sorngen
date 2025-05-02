------------------------------------------------------
-- SORNGEN VHDL FUNCTION GENERATOR 
-- Engine: 		0.1
-- Filename: 		ADD0.vhd
-- Author: 		n/a
-- Info: 		
-- SORN function
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

entity ADD0 is
       port(
       -- input port(s)
       input0 : IN std_logic_vector(6 downto 0);
input1 : IN std_logic_vector(6 downto 0);
       -- output port(s)
       output0 : OUT std_logic_vector(6 downto 0)
       );
end ADD0;

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
-- x1(0): [-inf,-2.0)
-- x1(1): [-2.0,-1.0)
-- x1(2): [-1.0,0.0)
-- x1(3): [0.0,0.0]
-- x1(4): (0.0,1.0]
-- x1(5): (1.0,2.0]
-- x1(6): (2.0,inf]

-- result  (output0) encoding
-- result(0): [-inf,-2.0)
-- result(1): [-2.0,-1.0)
-- result(2): [-1.0,0.0)
-- result(3): [0.0,0.0]
-- result(4): (0.0,1.0]
-- result(5): (1.0,2.0]
-- result(6): (2.0,inf]

------------------------------------------------------
architecture Behavior of ADD0 is     

-- components
-- none
-- signals
signal x0 : std_logic_vector(6 downto 0);
signal x1 : std_logic_vector(6 downto 0);
signal result : std_logic_vector(6 downto 0);

begin

-- instantiation/function
result(0) <= (x0(0) and x1(0)) or (x0(0) and x1(1)) or (x0(0) and x1(2)) or (x0(0) and x1(3)) or (x0(0) and x1(4)) or (x0(0) and x1(5)) or (x0(0) and x1(6)) or (x0(1) and x1(0)) or (x0(1) and x1(1)) or (x0(1) and x1(2)) or (x0(2) and x1(0)) or (x0(2) and x1(1)) or (x0(3) and x1(0)) or (x0(4) and x1(0)) or (x0(5) and x1(0)) or (x0(6) and x1(0));
result(1) <= (x0(0) and x1(4)) or (x0(0) and x1(5)) or (x0(0) and x1(6)) or (x0(1) and x1(2)) or (x0(1) and x1(3)) or (x0(1) and x1(4)) or (x0(2) and x1(1)) or (x0(2) and x1(2)) or (x0(3) and x1(1)) or (x0(4) and x1(0)) or (x0(4) and x1(1)) or (x0(5) and x1(0)) or (x0(6) and x1(0));
result(2) <= (x0(0) and x1(5)) or (x0(0) and x1(6)) or (x0(1) and x1(4)) or (x0(1) and x1(5)) or (x0(2) and x1(2)) or (x0(2) and x1(3)) or (x0(2) and x1(4)) or (x0(3) and x1(2)) or (x0(4) and x1(1)) or (x0(4) and x1(2)) or (x0(5) and x1(0)) or (x0(5) and x1(1)) or (x0(6) and x1(0));
result(3) <= (x0(0) and x1(6)) or (x0(1) and x1(5)) or (x0(2) and x1(4)) or (x0(3) and x1(3)) or (x0(4) and x1(2)) or (x0(5) and x1(1)) or (x0(6) and x1(0));
result(4) <= (x0(0) and x1(6)) or (x0(1) and x1(5)) or (x0(1) and x1(6)) or (x0(2) and x1(4)) or (x0(2) and x1(5)) or (x0(3) and x1(4)) or (x0(4) and x1(2)) or (x0(4) and x1(3)) or (x0(4) and x1(4)) or (x0(5) and x1(1)) or (x0(5) and x1(2)) or (x0(6) and x1(0)) or (x0(6) and x1(1));
result(5) <= (x0(0) and x1(6)) or (x0(1) and x1(6)) or (x0(2) and x1(5)) or (x0(2) and x1(6)) or (x0(3) and x1(5)) or (x0(4) and x1(4)) or (x0(4) and x1(5)) or (x0(5) and x1(2)) or (x0(5) and x1(3)) or (x0(5) and x1(4)) or (x0(6) and x1(0)) or (x0(6) and x1(1)) or (x0(6) and x1(2));
result(6) <= (x0(0) and x1(6)) or (x0(1) and x1(6)) or (x0(2) and x1(6)) or (x0(3) and x1(6)) or (x0(4) and x1(5)) or (x0(4) and x1(6)) or (x0(5) and x1(4)) or (x0(5) and x1(5)) or (x0(5) and x1(6)) or (x0(6) and x1(0)) or (x0(6) and x1(1)) or (x0(6) and x1(2)) or (x0(6) and x1(3)) or (x0(6) and x1(4)) or (x0(6) and x1(5)) or (x0(6) and x1(6));


-- assignments
x0 <= input0;
x1 <= input1;
output0 <= result;


end Behavior;