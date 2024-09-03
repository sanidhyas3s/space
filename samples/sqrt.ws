TAKES_INPUT_NUMBER_AND_PRINTS_INTEGER_PART_OF_SQRT--take-input	
		--store-0-to-heap-at-1   	
    
		 --push-placeholder-to-discard    
--label1:
   	
--discard 

--dup 
 --read-from-address-1   	
			--push-1   	
--add	   --store-to-heap-at-1   	
 
			 --read-from-address1   	
			--dup 
 --multiply	  
--sub	  	--dup 
 --ifnegjumpto1
		 	
--ifzerojumpto2
	  	 
--read-from-address1   	
			--push-1   	
--swap 
	--sub	  	--print-num	
 	--exit


--label2:
   	 
--read-from-address1   	
			--print-num	
 	--exit


