function work()
begin
    short a set S1 first smaller S2;
    short b set S2 first larger S1;
    short c set S2 second smaller S1;
    short d set S1 second larger S2;
end
return a add b add c add d;
