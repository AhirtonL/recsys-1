from __future__ import division
from operator import itemgetter 
from math import sqrt
from math import pow
import os


#get pearson similarity between two users
"""
pearson(uses[1],users[133])
"""

def euclidean(rating1,rating2):
	interact=dict()
	for key in rating1:
		if key in rating2:
			interact[key]=1
	n=len(interact)
	if n==0:
		return 0
	sum_euc=sum([pow(rating1[key]-rating2[key],2) for key in interact])

	return 1.0/(1+sqrt(sum_euc))

def pearson(rating1, rating2):
	interact=dict()
	for key in rating1:
		if key in rating2:
			interact[key] = 1
	n=len(interact)
	if n==0:
		return 0
	sum_x  =sum([rating1[key] for key in interact])
	sum_y  =sum([rating2[key] for key in interact])
	sum_x2 =sum([pow(rating1[key],2) for key in interact])
	sum_y2 =sum([pow(rating2[key],2) for key in interact])
	sum_xy =sum([rating1[key]*rating2[key] for key in interact])
	numerator=sum_xy-(sum_x * sum_y)/n
	denominator = sqrt(sum_x2 - pow(sum_x, 2) / n) * sqrt(sum_y2 - pow(sum_y, 2) / n)
	if denominator == 0:
		return 0
	else:
		val=numerator/denominator
		if val<-1:
			return -1
		elif val >1:
			return 1
		else:
			return val

def cosine(rating1,rating2):
	interact=dict()
	for key in rating1:
		if key in rating2:
			interact[key]=1
	n=len(interact)
	if n==0:
		return 0
	sum_x2 =sum([pow(rating1[key],2) for key in interact])
	sum_y2 =sum([pow(rating2[key],2) for key in interact])
	sum_xy =sum([rating1[key]*rating2[key] for key in interact])
	return sum_xy/(sqrt(sum_x2)*sqrt(sum_y2))



def adjust_cosine(rating1,rating2):
	interact=dict()
	for key in rating1:
		if key in rating2:
			interact[key]=1
	n=len(interact)
	if n==0:
		return 0
	ave_x_y=dict()
	for key in interact:
		ave_x_y.setdefault(key,0)
		ave_x_y[key] =(rating1[key]+rating2[key])/n

	sum_x2 =sum([pow(rating1[key]-ave_x_y[key],2) for key in interact])
	sum_y2 =sum([pow(rating2[key]-ave_x_y[key],2) for key in interact])
	sum_xy =sum([(rating1[key]-ave_x_y[key])*(rating2[key]-ave_x_y[key]) for key in interact])
	denominator=sqrt(sum_x2)*sqrt(sum_y2)
	if denominator == 0:
		return 0
	else:
		val=sum_xy/denominator
		if val<-1:
			return -1
		elif val >1:
			return 1
		else:
			return val


#get the average rank of one user
def average(rating):
	sum_ave=sum([rating[key] for key in rating])
	return sum_ave/len(rating)

#get user v similar to user u :<userid, pearson similarity value>
def getTopKMatches(users,u,K=10,similarity=pearson):
	W=[(v,similarity(users[u],users[v])) for v in users if u!=v ]
	W.sort(key=itemgetter(1))
	W.reverse()
	return W[0:K]

#recommend rated movies to a user u:<itemid,predicted rating>
def recommendation(users,u,K=10,similarity=pearson):
	ranks=dict()
	norms=dict()
	for v in users:
		if u ==v :
			continue
		sim=similarity(users[u],users[v])
		ave_v=average(users[v])
		if sim <=0:
			continue
		for item in users[v]:
			if item not in users[u].keys() :
				ranks.setdefault(item,0)
				ranks[item] +=sim*(users[v][item]-ave_v)
				norms.setdefault(item,0)
				norms[item] +=sim
	rankings=[(item,sum_rank/norms[item]) for item,sum_rank in ranks.items()]
	# rankings=[]
	# for item,sum_rank in ranks.items():
	# 	if norms[item] <=0:
	# 		rankings.append((item,0))
	# 	else :
	# 		rankings.append((item,sum_rank/norms[item]))
	rankings.sort(key=itemgetter(0))
	rankings.reverse()
	return rankings

#predict the rating given the userid u 
def predict(users,tests,u,ave_u,res):
	pred=dict()
	#ave_u=average(tests[u])
	#res=recommendation(users,u)	
	for item,real in tests[u].items():
		if u in users:
			if item in dict(res).keys():
				pred[item] =int(round(ave_u+dict(res)[item]))
	return pred

def predict_knn(users,tests,u,ave_u,K=10):
	ranks=dict()
	norms=dict()
	pred=dict()
	neighbors=getTopKMatches(users,u,K=10)
	for item,real in tests[u].items():
		if u in users:
			for i in range(len(neighbors)):
				v=neighbors[i][0]
				ave_v=average(users[v])
				simi_v=neighbors[i][1]
				if item in users[v]:
					ranks.setdefault(item,0)
					ranks[item] +=simi_v*(users[v][item]-ave_v)
					norms.setdefault(item,0)
					norms[item] +=simi_v
	for item,sum_rank in ranks.items():
		pred[item]=int(round(ave_u+sum_rank/norms[item]))
	return pred
	
#predict the rating given the userid u and movieid id 
def predict_user_item(users,tests,u,id,ave_u,res):
	#ave_u=average(tests[u])
	#res=recommendation(users,u)	
	if u in users:
		if id in dict(res).keys():
			return int(round(ave_u+dict(res)[id]))

#caluate RMSE
def rmse(true_val,pred_val):
	sum_rmse =sum(pow((true_val[i]-pred_val[i]),2) for i in range(len(true_val)))
	return round(sqrt(sum_rmse/len(true_val)),4)


def test():
	trainfile=os.getcwd()+os.sep+'ml-100k'+os.sep+'ua.base'
	testfile=os.getcwd()+os.sep+'ml-100k'+os.sep+'ua.test'


	# trainfile=os.getcwd()+os.sep+'ra.train'
	# testfile=os.getcwd()+os.sep+'ra.test'
	print 'Train data loading started : ' + trainfile
	print '...'
	trains=dict()
	#for line in open('./ml-100k/u1.base'):
	
	for line in open(trainfile):
		spl=line.strip().split()
		#spl=line.strip().split('::')
		if 4==len(spl):
				userid,itemid,rating,ts=spl
				trains.setdefault(int(userid),{})[int(itemid)]=float(rating)
	print 'Train data loading finished : ' + trainfile+'\n'
	
	print 'Test data loading started : ' + testfile
	print '...'
	tests=dict()
	
	#for line in open('./ml-100k/u1.test'):
	for line in open(testfile):
		spl=line.strip().split()
		#spl=line.strip().split('::')
		if 4==len(spl):
			userid,itemid,rating,ts=spl
			tests.setdefault(int(userid),{})[int(itemid)]=float(rating)	
	print 'Test data loading finished : ' + testfile+'\n'
	# print 'TopKMatches list(user,similarity_pearson) :'
	# top=getTopKMatches(trains,1,10)
	# for index,item in enumerate(top) :
	# 	print item

	# print 'Recommendation list(item,rank) for specific user :'+'\n'	
	# out=open('./ml-100k/recommend.txt','w')
	# for index,item in enumerate(recommendation(trains,181)) :
	# 	#print index,item
	# 	s=' '.join([str(item)])
	# 	out.write(s+'\n')
	# out.close()

	#predict(trains,tests,6)
	print '\n'+'Prediction...'
	# ave_u=average(tests[1])
	# pred=predict_knn(trains,tests,1,ave_u)
	# print pred
	true_val=[]
	pred_val=[]
	
	for user,item in tests.items():
		ave_u=average(tests[user])
		#res=recommendation(trains,user,similarity=cosine)
		res=recommendation(trains,user,similarity=euclidean)	
		pred=predict(trains,tests,user,ave_u,res)
		for item,val in sorted(tests[user].items(),key=itemgetter(0)):
			true_val.append(val)
			pr_right=val
			if item in pred.keys():
				if pred[item] <1 :
					pred_val.append(1)
					pr_right=1
				else :
					pred_val.append(int(pred[item]))
					pr_right=pred[item]
			else :
				pred_val.append(val)
	print len(pred_val)	

	# out=open('./ml-100k/prediction_ra_1.txt','w')
	# for user,item in tests.items():
	# 	ave_u=average(tests[user])
	# 	#res=recommendation(trains,user)	
	# 	pred=predict_knn(trains,tests,user,ave_u)
	# 	print len(pred)
	# 	for item,val in sorted(tests[user].items(),key=itemgetter(0)):
	# 		true_val.append(val)
	# 		pr_right=val
	# 		if item in pred.keys():
	# 			if pred[item] <1 :
	# 				pred_val.append(1)
	# 				pr_right=1
	# 			else :
	# 				pred_val.append(int(pred[item]))
	# 				pr_right=pred[item]
	# 		else :
	# 			pred_val.append(val)
	# #out.close()
	# print len(pred_val)	



    
	i=0
	out=open('./ml-100k/prediction_ra_euclidean.txt','w')
	for line in open(testfile):
		spl=line.strip().split()
		#spl=line.strip().split('::')
		if 4==len(spl):
			userid,itemid,rating,ts=spl
			s=' '.join([str(userid),str(itemid),str(pred_val[i]),str(ts)])
			i +=1
			out.write(s+'\n')

	print 'Output file writing finished ...'
	out.close()

	print 'RMSE=%s' %rmse(true_val,pred_val)

	# out=open('./ml-100k/prediction_181.txt','w')
	# ave_u=average(tests[181])
	# res=recommendation(trains,181)	
		
	# for item,val in sorted(predict(trains,tests,181,ave_u,res).items(),key=itemgetter(0)):
	# 	#print item,val
	# 	s=' '.join([str(181),str(item),str(val)])
	# 	out.write(s+'\n')
	# print 'Output file writing finished ...'
	# out.close()
	#print rmse([3,1,5,2,3],[2.3,0.9,4.9,0.9,1.5])

if __name__ == '__main__':
	test()
