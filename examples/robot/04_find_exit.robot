function moved(short value)
begin
    bool result set false;

    if value first smaller S0 then
        result set true;
    else
        result set result;

    if value first larger S0 then
        result set true;
    else
        result set result;
end
return result;


function side_move(short side)
begin
    short result set S0;

    if side first smaller S2 then
        result set left;
    else begin
        if side first smaller S4 then
            result set right;
        else
            result set move;
    end
end
return result;


function first_side(short orientation, short entry)
begin
    short side set S1;

    if orientation first smaller S2 then begin

        if entry first smaller S2 then
            side set S3;
        else begin
            if entry first smaller S4 then
                side set S5;
            else
                side set S1;
        end

    end else begin

        if entry first smaller S2 then
            side set S5;
        else begin
            if entry first smaller S4 then
                side set S1;
            else
                side set S3;
        end

    end
end
return side;


function second_side(short orientation, short entry)
begin
    short side set S1;

    if orientation first smaller S2 then begin

        if entry first smaller S2 then
            side set S5;
        else begin
            if entry first smaller S4 then
                side set S1;
            else
                side set S3;
        end

    end else begin

        if entry first smaller S2 then
            side set S3;
        else begin
            if entry first smaller S4 then
                side set S5;
            else
                side set S1;
        end

    end
end
return side;


function work()
begin
    short orientation set S1;

    short entry set S1;
    short side1 set S1;
    short side2 set S1;
    short side set S1;
    short result set S0;

    bool seeking set true;
    bool running set true;
    bool did_move set false;
    bool found set false;


    do begin

        result set right;

        if moved(result) then begin
            orientation set S4 sub orientation;
        end else begin
            seeking set false;
        end

    end while seeking;


    if orientation first smaller S2 then
        entry set S1;
    else
        entry set S5;


    do begin

        did_move set false;

        side1 set first_side(orientation entry);
        side2 set second_side(orientation entry);


        side set side1;
        result set side_move(side);

        if moved(result) then begin

            did_move set true;

        end else begin

            side set side2;
            result set side_move(side);

            if moved(result) then begin

                did_move set true;

            end else begin

                side set entry;
                result set side_move(side);

                if moved(result) then begin

                    did_move set true;

                end else begin

                    did_move set false;

                end

            end

        end


        if did_move then begin

            if side first smaller S2 then begin

                entry set S3;

            end else begin

                if side first smaller S4 then
                    entry set S1;
                else
                    entry set S5;

            end

            orientation set S4 sub orientation;

        end else begin

            found set true;
            running set false;

        end

    end while running;

end
return found;