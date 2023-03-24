import torch
from warnings import warn

__all__ = ["TDA_loss"]

def TDA_loss(H : torch.Tensor,
            labels : torch.Tensor,
            n_states : int,
            target_centers : list or torch.Tensor,
            target_sigmas : list or torch.Tensor,
            alpha : float = 1,
            beta : float = 100) -> torch.Tensor:
    """
    Compute a loss function as the distance from a simple Gaussian target distribution.
    
    Parameters
    ----------
    H : torch.Tensor
        Output of the NN
    labels : torch.Tensor
        Labels of the dataset
    n_states : int
        Number of states in the target
    target_centers : list or torch.Tensor
        Centers of the Gaussian targets
        Shape: (n_states, n_cvs)
    target_sigmas : list or torch.Tensor
        Standard deviations of the Gaussian targets
        Shape: (n_states, n_cvs)
    alpha : float, optional
        Centers_loss component prefactor, by default 1
    beta : float, optional
        Sigmas loss component prefactor, by default 100

    Returns
    -------
    torch.Tensor
        Total loss, centers loss, sigmas loss
    """
    if not isinstance(target_centers,torch.Tensor):
        target_centers = torch.Tensor(target_centers)
    if not isinstance(target_sigmas,torch.Tensor):
        target_sigmas = torch.Tensor(target_sigmas)
    
    loss_centers = torch.zeros_like(target_centers)
    loss_sigmas = torch.zeros_like(target_sigmas)
    for i in range(n_states):
        # check which elements belong to class i
        if not torch.nonzero(labels == i).any():
            raise ValueError(f'State {i} was not represented in this batch! Either use bigger batch_size or a more equilibrated dataset composition!')
        else:
            H_red = H[torch.nonzero(labels == i, as_tuple=True)]
            
            # compute mean and standard deviation over the class i
            mu = torch.mean(H_red, 0)
            if len(torch.nonzero(labels == i)) == 1:
                warn(f'There is only one sample for state {i} in this batch! Std is set to 0, this may affect the training! Either use bigger batch_size or a more equilibrated dataset composition!')
                sigma = 0
            else:
                sigma = torch.std(H_red, 0)

        # compute loss function contributes for class i
        loss_centers[i] = alpha*(mu - target_centers[i]).pow(2)
        loss_sigmas[i] = beta*(sigma - target_sigmas[i]).pow(2)
        
        
    # get total model loss   
    loss_centers = torch.sum(loss_centers)
    loss_sigmas = torch.sum(loss_sigmas) 
    loss = loss_centers + loss_sigmas  

    return loss, loss_centers, loss_sigmas

