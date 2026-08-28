function work()
begin
    short i set S0;
    short sum set S0;
    do
    begin
        i set i add S1;
        sum set sum add i;
    end
    while i first smaller S5;
end
return sum;
