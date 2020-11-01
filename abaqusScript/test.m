function u = tinhChuyenVi(n,p1,p2,p3)
    fid = fopen('parameters.csv', 'wt');
    fprintf(fid,"0\n2.5\nNone\n");
    fprintf(fid,"12\n");
    fprintf(fid, '%f\n', p3);
    fprintf(fid, '%f\n', p3);
    fprintf(fid, '%f\n', p2);
    fprintf(fid, '%f\n', p2);
    fprintf(fid, '%f\n', p2);
    fprintf(fid, '%f\n', p1);
    fprintf(fid, '9\n');
    fprintf(fid, '%d\n', n);
    fprintf(fid, '%f\n', p3);
    fprintf(fid, '2\n0\n2\n0.5\n0.1\n0.01\n3');
    fclose(fid);
    !abaqus cae script=./autoParametric2DnoGUI.py
    transpose = csvread('transpose_output.csv')
    disp("gia tri chuyen vi:")
    disp(transpose)
end

