function fibonacci(short n)
begin
    short result set n;
    short one set S1, two set S2;
    short n1 set S0, n2 set S0, r1 set S0, r2 set S0;

    if n first larger one then
    begin
        n1 set n sub one;
        n2 set n sub two;
        r1 set fibonacci(n1);
        r2 set fibonacci(n2);
        result set r1 add r2;
    end
    else
        result set result;
end
return result;

function work()
begin
    short n set S8;
    short result set fibonacci(n);
end
return result;
