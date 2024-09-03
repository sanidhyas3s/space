push0   
takeinput	
		duplicate 
 JMPifequalto0tolabel5
	  	 	
duplicate 
 JMPifnegativetolabel6
		 		 
marklabel1
   	
duplicate 
 JMPifequalto0to8
	  	 
duplicate 
 push1   	
swap 
	subtract	  	JMP2
 
 	
marklabel2
   	 
pop 

marklabel3
   		
swap 
	duplicate 
 JMPifequalto0to14
	  	  
multiply	  
JMP9
 
 		
marklabel4
   	  
swap 
	print	
 	end


marklabel5
   	 	
push1   	
print	
 	end


marklabel6
   		 
push-1  		
print	
 	end


