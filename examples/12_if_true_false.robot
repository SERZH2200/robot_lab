function work()
begin
    short result set S0;
    if true then
        result set S5;
    else
        result set S-5;

    if false then
        result set S100;
    else
        result set result add S2;
end
return result;
