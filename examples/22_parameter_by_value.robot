function change(short value)
begin
    value set S99;
end
return value;

function work()
begin
    short original set S5;
    change(original);
end
return original;
