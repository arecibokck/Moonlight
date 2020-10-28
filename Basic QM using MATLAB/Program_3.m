%****************************************************************
% Program 3: Matrix representation of differential operators,
% Solving for Eigenvectors & Eigenvalues of Infinite SquareWell
%****************************************************************
%

% Parameters for solving problem in the interval 0 < x < L
L = 2*pi;                   % Interval Length
N = 100;                    % No. of coordinate points
x = linspace(0,L,N)';       % Coordinate vector
dx = x(2) - x(1);           % Coordinate step

% Three-point finite-difference representation of Laplacian
Lap = (diag(ones((N-1),1),1) - 2*diag(ones(N,1),0) + diag(ones((N-1),1),-1))/(dx^2);
% Next modify Lap so that it is consistent with f(0) = f(L) = 0
Lap(1,1) = 0; Lap(1,2) = 0; Lap(2,1) = 0;    % So that f(0) = 0
Lap(N,N-1) = 0; Lap(N-1,N) = 0; Lap(N,N) = 0;% So that f(L) = 0

% Total Hamiltonian where hbar=1 and m=1
hbar = 1; m = 1; H = -(1/2)*(hbar^2/m)*Lap;
% Solve for eigenvector matrix V and eigenvalue matrix E of H
[V,E] = eig(H);

% Plot lowest 3 eigenfunctions
figure(1)
plot(x,V(:,3),'r',x,V(:,4),'b',x,V(:,5),'k'); shg;

figure(2)
imagesc(E) % display eigenvalue matrix

figure(3)
plot(diag(E))% display a vector containing the eigenvalues