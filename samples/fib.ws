--push0   
--push1   	
--take-input	
		--dup 
 --ifnegjumpto1
		 	
--dup 
 --ifzerogoto1
	  	
--push1   	
--swap 
	--sub	  	--dup 
 --ifzerogoto2
	  	 
--label3
   		
--push1   	
--swap 
	--sub	  	--dup 
 --ifzerogoto4
	  	  
--swap 
	--dup 
 --copy4th 	  	  
--add	   --copy3rd 	  		
--goto3
 
 		
--label4
   	  
--discard 

--print-num	
 	--exit


--label1
   	
--push(-1)  		
--print-num	
 	--exit


--label2
   	 
--push0   
--print-num	
 	--exit


