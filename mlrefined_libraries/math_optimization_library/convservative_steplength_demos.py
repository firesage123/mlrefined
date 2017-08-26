# import custom JS animator
from mlrefined_libraries.JSAnimation_slider_only import IPython_display_slider_only

# import standard plotting and animation
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import gridspec
from IPython.display import clear_output
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
from matplotlib.text import Annotation
from mpl_toolkits.mplot3d.proj3d import proj_transform

# import autograd functionality
from autograd import grad as compute_grad   # The only autograd function you may ever need
import autograd.numpy as np
import math
import time

# simple first order taylor series visualizer
class visualizer:
    '''
    Illustrates how conservative steplength rules work in general.
    ''' 
     
    ######## gradient descent ########
    # run gradient descent 
    def run_gradient_descent(self):
        w = self.w_init
        self.w_hist = []
        self.w_hist.append(w)
        w_old = np.inf
        j = 0
        for j in range(int(self.max_its)):
            # update old w and index
            w_old = w
            
            # plug in value into func and derivative
            grad_eval = self.grad(w)
            
            ### normalized or unnormalized? ###
            if self.version == 'normalized':
                grad_norm = np.linalg.norm(grad_eval)
                if grad_norm == 0:
                    grad_norm += 10**-6*np.sign(2*np.random.rand(1) - 1)
                grad_eval /= grad_norm
                
            ### check what sort of steplength rule to employ ###
            alpha = 0
            if self.steplength == 'diminishing':
                alpha = 1/(1 + j)
            elif self.steplength == 'backtracking':
                alpha = self.backtracking(w,grad_eval)
            elif self.steplength == 'exact': 
                alpha = self.exact(w,grad_eval)
            else:
                alpha = float(self.steplength)            
            
            # take gradient descent step
            w = w - alpha*grad_eval
            
            # record
            self.w_hist.append(w)

    # backtracking linesearch module
    def backtracking(self,w,grad_eval):
        # set input parameters
        alpha = 1
        t = 0.5
        
        # compute initial function and gradient values
        func_eval = self.g(w)
        grad_norm = np.linalg.norm(grad_eval)**2
        
        # loop over and tune steplength
        while self.g(w - alpha*grad_eval) > func_eval - alpha*0.5*grad_norm:
            alpha = t*alpha
        return alpha

    # exact linesearch module
    def exact(self,w,grad_eval):
        # set parameters of linesearch at each step
        valmax = 3
        num_evals = 100
        
        # set alpha range
        alpha_range = np.linspace(0,valmax,num_evals)
        
        # evaluate function over direction and alpha range, grab alpha giving lowest eval
        steps = [(w - alpha*grad_eval) for alpha in alpha_range]
        func_evals = np.array([self.g(s) for s in steps])
        ind = np.argmin(func_evals)
        best_alpha = alpha_range[ind]
        
        return best_alpha
    
    # visualize descent on multi-input function
    def run(self,g,w_init,steplength_vals,max_its,**kwargs):
        # count up steplength vals
        step_count = len(steplength_vals)
        
        ### input arguments ###        
        self.g = g
        self.max_its = max_its
        self.grad = compute_grad(self.g)              # gradient of input function

        wmax = 1
        if 'wmax' in kwargs:
            wmax = kwargs['wmax'] + 0.5

        view = [20,-50]
        if 'view' in kwargs:
            view = kwargs['view']

        axes = False
        if 'axes' in kwargs:
            axes = kwargs['axes']

        plot_final = False
        if 'plot_final' in kwargs:
            plot_final = kwargs['plot_final']

        num_contours = 10
        if 'num_contours' in kwargs:
            num_contours = kwargs['num_contours']

        # version of gradient descent to use (normalized or unnormalized)
        self.version = 'unnormalized'
        if 'version' in kwargs:
            self.version = kwargs['version']
            
        # get initial point 
        self.w_init = np.asarray([float(s) for s in w_init])
            
        # take in user defined maximum number of iterations
        self.max_its = max_its
            
        ##### construct figure with panels #####
        # construct figure
        fig = plt.figure(figsize = (9,1 + (2.25)*step_count))

        # remove whitespace from figure
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # remove whitespace

        # create subplot with 3 panels, plot input function in center plot
        gs = gridspec.GridSpec(step_count, 2, width_ratios=[2,1]) 
        
        # loop over steplengths, plot panels for each
        count = 0
        for step in steplength_vals:
            
            ax = plt.subplot(gs[2*count]); 
            ax2 = plt.subplot(gs[2*count + 1]); 

            #### run local random search algorithm ####
            self.w_hist = []
            self.steplength = steplength_vals[count]
            self.run_gradient_descent()
            count+=1
        
            # set viewing limits on contour plot
            xvals = [self.w_hist[s][0] for s in range(len(self.w_hist))]
            xvals.append(self.w_init[0])
            yvals = [self.w_hist[s][1] for s in range(len(self.w_hist))]
            yvals.append(self.w_init[1])
            xmax = max(xvals)
            xmin = min(xvals)
            xgap = (xmax - xmin)*0.1
            ymax = max(yvals)
            ymin = min(yvals)
            ygap = (ymax - ymin)*0.1
            xmin -= xgap
            xmax += xgap
            ymin -= ygap
            ymax += ygap
        
            #### define input space for function and evaluate ####
            w1 = np.linspace(xmin,xmax,200)
            w2 = np.linspace(ymin,ymax,200)
            w1_vals, w2_vals = np.meshgrid(w1,w2)
            w1_vals.shape = (len(w1)**2,1)
            w2_vals.shape = (len(w2)**2,1)
            h = np.concatenate((w1_vals,w2_vals),axis=1)
            func_vals = np.asarray([g(s) for s in h])
            w1_vals.shape = (len(w1),len(w1))
            w2_vals.shape = (len(w2),len(w2))
            func_vals.shape = (len(w1),len(w2)) 

            ### make contour right plot - as well as horizontal and vertical axes ###
            ax.contour(w1_vals, w2_vals, func_vals,num_contours,colors = 'k')
            if axes == True:
                ax.axhline(linestyle = '--', color = 'k',linewidth = 1)
                ax.axvline(linestyle = '--', color = 'k',linewidth = 1)

            # colors for points
            s = np.linspace(0,1,len(self.w_hist[:round(len(self.w_hist)/2)]))
            s.shape = (len(s),1)
            t = np.ones(len(self.w_hist[round(len(self.w_hist)/2):]))
            t.shape = (len(t),1)
            s = np.vstack((s,t))
            colorspec = []
            colorspec = np.concatenate((s,np.flipud(s)),1)
            colorspec = np.concatenate((colorspec,np.zeros((len(s),1))),1)

            ### plot function decrease plot in right panel
            for j in range(len(self.w_hist)):  
                w_val = self.w_hist[j]
                g_val = self.g(w_val)

                # plot in left panel
                ax.scatter(w_val[0],w_val[1],s = 30,c = colorspec[j],edgecolor = 'k',linewidth = 1.5*math.sqrt((1/(float(j) + 1))),zorder = 3)

                ax2.scatter(j,g_val,s = 30,c = colorspec[j],edgecolor = 'k',linewidth = 0.7,zorder = 3)            # plot point of tangency

                # plot connector between points for visualization purposes
                if j > 0:
                    w_old = self.w_hist[j-1]
                    w_new = self.w_hist[j]
                    g_old = self.g(w_old)
                    g_new = self.g(w_new)
                    ax.plot([w_old[0],w_new[0]],[w_old[1],w_new[1]],color = colorspec[j],linewidth = 2.5,alpha = 0.8,zorder = 2)      # plot approx
                    ax2.plot([j-1,j],[g_old,g_new],color = colorspec[j],linewidth = 2,alpha = 0.4,zorder = 1)      # plot approx

            # clean panels
            title = self.steplength
            if type(self.steplength) == float:
                title = r'$\alpha = $' + str(self.steplength)
            ax.set_title(title,fontsize = 12)
            ax.set_xlabel('$w_1$',fontsize = 12)
            ax.set_ylabel('$w_2$',fontsize = 12,rotation = 0)
            ax.axhline(y=0, color='k',zorder = 0,linewidth = 0.5)
            ax.axvline(x=0, color='k',zorder = 0,linewidth = 0.5)
            ax2.axhline(y=0, color='k',zorder = 0,linewidth = 0.5)
            ax2.set_xlabel('iteration',fontsize = 12)
            ax2.set_ylabel(r'$g(w)$',fontsize = 12,rotation = 0,labelpad = 25)

            ax.set_xlim([xmin,xmax])
            ax.set_ylim([ymin,ymax])

        # plot
        plt.show()
   