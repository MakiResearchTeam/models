from makiflow.layers import *
from makiflow.base import MakiTensor

def identity_block(x : MakiTensor, block_id: int, unit_id: int, num_block: int, in_f=None, use_bias=False,activation=tf.nn.relu):
    """
        Parameters
        ----------
            in_f : int
                Number of input feature maps. By default None (shape will be getted from tensor)
            activation : tensorflow function
                The function of activation, by default tf.nn.relu
            use_bias : bool
                Use bias on layers or not
        
        Returns
        ---------
            x : MakiTensor
                Output MakiTensor
            in_f : int
                Output number of feature maps 
    """

    prefix_name = 'block' + str(block_id) + '/unit_' + str(unit_id)
    if in_f is None:
        in_f = x.get_shape()[-1]

    reduction = int(in_f / 4)

	mx = ConvLayer(kw=1, kh=1, in_f=in_f, out_f=reduction, activation=None, 
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv1/weights')(x)
	                                                                            
	mx = BatchNormLayer(D=reduction, name=prefix_name + '/bottleneck_v1/conv1/BatchNorm')(mx)
	mx = ActivationLayer(activation=activation, name=prefix_name + '/bottleneck_v1/conv1/activ')(mx)

	mx = ConvLayer(kw=3, kh=3, in_f=reduction, out_f=reduction, activation=None,
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv2/weights')(mx)
	                                                                   
	mx = BatchNormLayer(D=reduction, name=prefix_name + '/bottleneck_v1/conv2/BatchNorm')(mx)
	mx = ActivationLayer(activation=activation, name=prefix_name + '/bottleneck_v1/conv2/activ')(mx)

	mx = ConvLayer(kw=1, kh=1, in_f=reduction, out_f=in_f, activation=None,
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv3/weights')(mx)
	                                                                            
	mx = BatchNormLayer(D=in_f, name=prefix_name + '/bottleneck_v1/conv3/BatchNorm')(mx)

	x = SumLayer(name='add' + str(num_block))([mx,x])

	return x, in_f

def conv_block(x : MakiTensor, block_id: int, unit_id: int, num_block: int, in_f=None, use_bias=False, activation=tf.nn.relu, stride=2):
    """
        Parameters
        ----------
            in_f : int
                Number of input feature maps. By default None (shape will be getted from tensor)
            activation : tensorflow function
                The function of activation, by default tf.nn.relu
            use_bias : bool
                Use bias on layers or not
        
        Returns
        ---------
            x : MakiTensor
                Output MakiTensor
            increase : int
                Output number of feature maps 
    """

    prefix_name = 'block' + str(block_id) + '/unit_' + str(unit_id)

    if in_f is None:
        in_f = x.get_shape()[-1]

    reduction = min(64, int(in_f / 2))
    increase = reduction * 2  if reduction == 64 else reduction * 4

	mx = ConvLayer(kw=1, kh=1, in_f=in_f, out_f=reduction, stride=stride, activation=None, 
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv1/weights')(x)
	                                                                           
	mx = BatchNormLayer(D=reduction, name=prefix_name + '/bottleneck_v1/conv1/BatchNorm')(mx)
	mx = ActivationLayer(activation=activation, name=prefix_name + '/bottleneck_v1/conv1/activ')(mx)

	mx = ConvLayer(kw=3, kh=3, in_f=reduction, out_f=reduction, activation=None,
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv2/weights')(mx)
	                                                                            
	mx = BatchNormLayer(D=reduction, name=prefix_name + '/bottleneck_v1/conv2/BatchNorm')(mx)
	mx = ActivationLayer(activation=activation, name=prefix_name + '/bottleneck_v1/conv2/activ')(mx)

	mx = ConvLayer(kw=1, kh=1, in_f=reduction, out_f=increase, activation=None,
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/conv3/weights')(mx)
	                                                                            
	mx = BatchNormLayer(D=increase, name=prefix_name + '/bottleneck_v1/conv3/BatchNorm')(mx)

	sx = ConvLayer(kw=1, kh=1, in_f=in_f, out_f=increase, stride=stride, activation=None,
                                use_bias=use_bias, name=prefix_name + '/bottleneck_v1/shortcut/weights')(x)
	                                                                            
	sx = BatchNormLayer(D=increase, name=prefix_name + '/bottleneck_v1/shortcut/BatchNorm')(sx)

	x = SumLayer(name='add' + str(num_block))([mx,sx])

	return x, increase


def without_pointwise_IB(x : MakiTensor, block_id: int, unit_id: int, num_block: int, in_f=None, use_bias=False,activation=tf.nn.relu):
    """
        Parameters
        ----------
            in_f : int
                Number of input feature maps. By default None (shape will be getted from tensor)
            activation : tensorflow function
                The function of activation, by default tf.nn.relu
            use_bias : bool
                Use bias on layers or not
        
        Returns
        ---------
            x : MakiTensor
                Output MakiTensor
            in_f : int
                Output number of feature maps
    """

    prefix_name = 'stage' + str(stage_id) + '_unit' + str(unit_id) + '_'

    if in_f is None:
        in_f = x.get_shape()[-1]

	mx = BatchNormLayer(D=in_f, name=prefix + 'bn1')(x)
	                                    
	mx = ActivationLayer(activation=activation, name=prefix + 'activation_1')(mx)

	mx = ZeroPaddingLayer(padding=[[1,1],[1,1]], name=prefix + 'zero_pad_1')(mx)

	mx = ConvLayer(kw=3, kh=3, in_f=in_f, out_f=in_f, activation=None,
								padding='VALID', use_bias=use_bias, name=prefix + 'conv1')(mx)
	                                                                                
	mx = BatchNormLayer(D=in_f, name=prefix + 'bn2')(mx)
	
	mx = ActivationLayer(activation=activation, name=prefix + 'activation_2')(mx)

	mx = ZeroPaddingLayer(padding=[[1,1],[1,1]], name=prefix + 'zero_pad_2')(mx)

	mx = ConvLayer(kw=3, kh=3, in_f=in_f, out_f=in_f, activation=None,
								padding='VALID', use_bias=use_bias, name=prefix + 'conv2')(mx)                        

	x = SumLayer(name='add' + str(num_block))([mx,x])

	return x, in_f


def without_pointwise_CB(x : MakiTensor, block_id: int, unit_id: int, num_block: int, in_f=None, use_bias=False, activation=tf.nn.relu, stride=2, out_f=None):
    """
        Parameters
        ----------
            in_f : int
                Number of input feature maps. By default is None (shape will be getted from tensor)
            out_f : int
                Number of output feature maps. By default is None which means out_f = 2 * in_f
            activation : tensorflow function
                The function of activation. By default tf.nn.relu
            use_bias : bool
                Use bias on layers or not
        
        Returns
        ---------
            x : MakiTensor
                Output MakiTensor
            out_f : int
                Output number of feature maps
    """
	prefix = 'stage' + str(stage_id) + '_unit' + str(unit_id) + '_'

    if in_f is None:
        in_f = x.get_shape()[-1]

	if out_f is None:
		out_f = int(2*in_f)
	else:
		out_f = out_f

	x = BatchNormLayer(D=in_f, name=prefix + 'bn1')(x)
	x = ActivationLayer(activation=activation, name=prefix + 'activation_1')(x)

	mx = ZeroPaddingLayer(padding=[[1,1],[1,1]], name=prefix + 'zero_pad_1')(x)

	mx = ConvLayer(kw=3, kh=3, in_f=in_f, out_f=out_f, activation=None, stride=stride,
									padding='VALID', use_bias=use_bias, name=prefix + 'conv1')(mx)
	                                                                            
	mx = BatchNormLayer(D=out_f, name=prefix + 'bn2')(mx)
	mx = ActivationLayer(activation=activation, name=prefix + 'activation_2')(mx)

	mx = ZeroPaddingLayer(padding=[[1,1],[1,1]], name=prefix + 'zero_pad_2')(mx)
	mx = ConvLayer(kw=3, kh=3, in_f=out_f, out_f=out_f, activation=None,
									padding='VALID', use_bias=use_bias, name=prefix + 'conv2')(mx)
	                                                                            

	sx = ConvLayer(kw=1, kh=1, in_f=in_f, out_f=out_f, stride=stride,
									padding='VALID', activation=None, use_bias=use_bias, name=prefix + 'sc/conv')(x)
	                                                                           
	x = SumLayer(name='add' + str(num_block))([mx,sx])

	return x, out_f