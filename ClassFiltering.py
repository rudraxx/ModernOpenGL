import numpy as np

class ClassFiltering():

    num_samples = 3
    iCount = 0
    flag_buffer_ready = False
    avg_value = np.zeros(shape=(1,3),dtype=np.float32)

    def __init__(self, num_samples):
        self.num_samples = num_samples

        self.data_buffer = np.zeros(shape=(self.num_samples,3),dtype=np.float32)
        self.iCount = 0

    def updateBuffer(self,new_sample):

        # Update the buffer
        for i in range(0,self.num_samples-1):
            self.data_buffer[i,:] = self.data_buffer[i+1,:]

        # Update the last entry as well
        self.data_buffer[self.num_samples-1, :] = new_sample

        # While the buffer is filling up, send out the current value
        if not self.flag_buffer_ready:
            # Update the buffer count value
            if self.iCount< self.num_samples:
                self.iCount +=1

                # Use the current estimate as the avf value
                self.avg_value = new_sample
                # print(self.avg_value)
                return

            else:
                self.flag_buffer_ready = True
                # print(self.avg_value)
                return


        # Calculate average value
        a = np.sum(self.data_buffer[:,0]) / self.num_samples
        b = np.sum(self.data_buffer[:,1]) / self.num_samples
        c = np.sum(self.data_buffer[:,2]) / self.num_samples

        self.avg_value = np.array([a,b,c])
        print(self.avg_value)





