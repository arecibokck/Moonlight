%****************************************************************
% Program 1: Numerical Integration and Plotting using MATLAB
%****************************************************************
N=1000000;               % No. of points
L=500;                   % Range of x: from -L to L
x=linspace(-L,L,N)';     % Generate column vector with N
                         % x values ranging from -L to L
dx=x(2)-x(1);            % Distance between adjacent points

% Alternative Trial functions:
% To select one, take out the comment command % at the beginning.
% y=exp(-x.^2/16);                 % Gaussian centered at x=0
% y=((2/pi)^0.5)*exp(-2*(x-1).^2); % Normed Gaussian at x=1
% y=(1-x.^2).^-1;                  % Symmetric fcn which blows up at x=1
% y=(cos(pi*x)).^2;                % Cosine fcn
% y=exp(i*pi*x);                   % Complex exponential
% y=sin(pi*x/L).*cos(pi*x/L);      % Product of sinx times cosx
% y=sin(pi*x/L).*sin(pi*x/L);      % Product of sin(nx) times sin(mx)
% A=100; y=sin(x*A)./(pi*x);       % Rep. of delta fcn
% A=20; y=(sin(x*A).^2)./(pi*(A*x.^2)); % Another rep. of delta fcn

% Observe: numerically a function y(x) is represented by a vector!
% Plot a vector/function
plot(x,y);                             % Plots vector y vs. x
%plot(x,real(y),’r’, x, imag(y), ’b’); % Plots real&imag yvs. x
axis([-2 2 0 7]);    % Optimized axis parameters for sinx^2/pix^2
%axis([-2 2 -8 40]); % Optimized axis parameters for sinx/pix
% Numerical Integration
sum(y)*dx        % Simple numerical integral of y
trapz(y)*dx      % Integration using trapezoidal rule