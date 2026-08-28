function change(vector of short values)
begin
    values[0] set S99;
end
return values[0];

function work()
begin
    vector of short original set {S1, S2, S3};
    change(original);
end
return original[0];
