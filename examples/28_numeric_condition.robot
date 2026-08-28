function work()
begin
    short result set S0;
    if S5 then
        result set result add S1;
    else
        result set result add S100;

    if S-5 then
        result set result add S100;
    else
        result set result add S2;

    if S0 then
        result set result add S100;
    else
        result set result add S100;
end
return result;
