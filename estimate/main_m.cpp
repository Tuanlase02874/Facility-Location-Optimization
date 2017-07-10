#include <ilcplex/ilocplex.h>
#include <stdlib.h>
#include <time.h>
#include <ctime>
#include <sys/time.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>


using namespace std;

ILOSTLBEGIN


static void readData(char * fileName, IloInt& optNum, IloInt& assNum, IloIntArray& optCode, IloNumArray & optProb, IloIntArray& assSize)
{
    string line;
    ifstream file(fileName);

    if(file.is_open())
    {
        //First line is ignored
        getline(file, line);

        //Second line is the number of options
        getline(file, line);
        optNum = atoi(line.c_str());

        //Third and fourth lines are ignored
        getline(file, line);
        getline(file, line);

        //Reading assortments
        assNum = 0;
        bool codeRead = true;
        while(getline(file, line))
        {


            if(codeRead)
            {
                //Get code of assortments
                stringstream ss;
                ss.str(line);
                string item;

                int size = 0;
                while(getline(ss, item, ' '))
                {
                    int num = atoi(item.c_str());
                    optCode.add(num);

                    size++;
                }

                //Update counter for the number of assortments
                assNum++;

                //Update assortment size
                assSize.add(size);

                //Update flip variable
                codeRead = false;
            }else
            {
                stringstream ss;
                ss.str(line);
                string item;

                while(getline(ss, item, ' '))
                {
                    double num = atof(item.c_str());
                    optProb.add(num);
                }

                codeRead = true;
            }


        }
    }

    file.close();
}


unsigned getTimeInMilli()
{
    struct timeval tv;
    if(gettimeofday(&tv, NULL) != 0)
    {
        return 0;
    }
    return (tv.tv_sec * 1000) + (tv.tv_usec/1000);
}

int
main(int argc, char **argv)
{
   IloEnv env;
   try {

       unsigned t1 = getTimeInMilli();

       IloInt i,j,k,p;

       IloInt optNum;
       IloInt assNum;
       IloIntArray optCode(env);
       IloIntArray assSize(env);
       IloNumArray optProb(env);


       //Reading inputs
       readData(argv[1], optNum, assNum, optCode, optProb, assSize);

       cout <<"Number of options: " << optNum << endl;
       cout << "Size of codes: " << optCode.getSize() << endl;
       for(i = 0; i < optCode.getSize(); i++)
       {
           cout << optCode[i] << " ";
       }cout << endl;

       cout << "Size of probabilities: " << optProb.getSize() << endl;
       for(i = 0; i < optProb.getSize(); i++)
       {
           cout << optProb[i] << " ";
       }cout << endl;

       cout << "Number of assortments: " << assNum << endl;
       cout << "Sizes of assortments: ";
       for(i = 0; i < assSize.getSize(); i++)
       {
           cout << assSize[i] << " ";
       }cout << endl;


       //List of ranking data
       IloArray<IloIntArray> rankDataLst(env);

       //Initialize the list of ranking data with a ranking data
       IloIntArray rankInstance(env);
       for(i = 0; i < optNum; i++)
       {
           rankInstance.add(i);
       }
       rankDataLst.add(rankInstance);

       //Matrix A
       IloArray<IloIntArray> A(env, rankDataLst.getSize());
       for(i = 0; i < rankDataLst.getSize(); i++)
       {
           A[i] = IloIntArray(env, optCode.getSize());
           IloInt counter = 0;
           for(j = 0; j < assNum; j++)
           {
               //Find highest option in the assortment
               IloInt highestOpt = optCode[counter];
               for(k = 0; k < rankDataLst[i].getSize(); k++)
               {
                   IloInt opt1 = rankDataLst[i][k];
                   for(p = 0; p < assSize[j]; p++)
                   {
                       IloInt opt2 = optCode[counter+p];
                       if(opt1 == opt2)
                       {
                           highestOpt = p;

                           //Break
                           p = assSize[j];
                           k = rankDataLst[i].getSize();
                       }
                   }
               }

               for(k = 0; k < assSize[j]; k++)
               {
                   A[i][counter + k] = 0;
               }

               A[i][counter +highestOpt] = 1;

               //Update counter
               counter += assSize[j];

           }
       }

//       cout << "Matrix A: " << endl;
//       for(i = 0; i < A.getSize(); i++)
//       {
//           for(j = 0; j < A[i].getSize(); j++)
//           {
//               cout << A[i][j] << " ";
//           }cout << endl;
//       }


       IloNumVarArray lamda_global(env,ILOFLOAT);
       ///COLUMN GENERATION
       int it = 0;
       bool stop = false;
       while(it < 500 && !stop)
       {
           it++;

           cout <<"-------------------Iteration: " << it << endl;


           ///    RESTRICTED MASTER PROBLEM ///

           IloModel resMasterModel (env);
           IloCplex resMasterSolver(resMasterModel);

           //Decision variables
           IloNumVarArray pE(env, optProb.getSize(), 0, IloInfinity, ILOFLOAT);
           IloNumVarArray nE(env, optProb.getSize(), 0, IloInfinity, ILOFLOAT);
           IloNumVarArray lamda(env, A.getSize(), 0, 1, ILOFLOAT);


           //Objective
           IloExpr masterObj(env, 0);
           for(i = 0; i< pE.getSize(); i++)
           {
               masterObj += pE[i] + nE[i];
           }
           resMasterModel.add(IloMinimize(env, masterObj));
           masterObj.end();


           //Constraints
           IloRangeArray constraints(env);

           IloExpr expr(env, 0);

           for(i = 0; i < lamda.getSize(); i++)
           {
               expr += lamda[i];
           }

           IloRange cons = expr == 1;
           constraints.add(cons);

           expr.end();

           for(i = 0; i < optProb.getSize(); i++)
           {
               IloExpr expr(env, 0);
               for(j = 0; j < A.getSize(); j++)
               {
                   expr += A[j][i] * lamda[j];
               }

               expr += pE[i] - nE[i];

               expr -= optProb[i];

               IloRange cons = expr == 0;
               constraints.add(cons);

               expr.end();
           }



           for(i = 0; i < constraints.getSize(); i++)
           {
               resMasterModel.add(constraints[i]);
           }


           //Solve restricted master problem
           resMasterSolver.setParam(IloCplex::MIPDisplay, 1);
           resMasterSolver.solve();

           cout << "***********************************************************" << endl;
           cout << "Objective value of restricted master problem: " << resMasterSolver.getObjValue() << endl;
           cout << "Lamda: ";
           for(i = 0; i < lamda.getSize(); i++)
           {
               cout << resMasterSolver.getValue(lamda[i]) << " ";
           }cout << endl;
           cout << "***********************************************************" << endl;



//           for(i = 0; i < lamda.getSize(); i++)
//           {
//               lamda_global[i] = resMasterSolver.getValue(lamda[i]);
//           }//cout << endl;
//           //cout << "***********************************************************" << endl;

           //Get duals
           IloNumArray price(env, optProb.getSize());
           //cout << "PRICE: ";
           for (i = 0; i < price.getSize(); i++)
           {
               price[i] = resMasterSolver.getDual(constraints[i+1]);
               //cout << price[i] << " ";
           }//cout << endl;

           IloNum v = resMasterSolver.getDual(constraints[0]);
           //cout << "v: " << v << endl;

           ///     SUBPROBLEM   ///

           IloModel subProblemModel (env);
           IloCplex subProblemSolver(subProblemModel);

           //Decision variables
           IloArray<IloNumVarArray> z(env, optNum);
           for(i = 0; i < optNum; i++)
           {
               z[i] = IloNumVarArray(env, optNum, 0, 1, ILOINT);
           }

           IloNumVarArray a(env, optProb.getSize(), 0, IloInfinity, ILOFLOAT);

           //Objective
           IloExpr subProblemObj(env, 0);
           for(i = 0; i < optProb.getSize(); i++)
           {
               subProblemObj -= price[i] * a[i];
           }
           subProblemObj -= v;

           subProblemModel.add(IloMinimize(env, subProblemObj));
           subProblemObj.end();

           //Constrains
           for(i = 0; i < optNum; i++)
           {
               for(j = 0; j < optNum; j++)
               {
                   if(i != j)
                   {
                       subProblemModel.add(z[i][j] + z[j][i] == 1);

                       for(k = 0; k < optNum; k++)
                       {
                           if(i != k && j != k)
                           {
                               subProblemModel.add(z[i][j] + z[j][k] - 1 <= z[i][k]);
                           }
                       }
                   }
               }
           }


           IloInt counter = 0;
           for(i = 0; i < assNum; i++)
           {
               IloExpr expr(env, 0);
               for(j = 0; j < assSize[i]; j++)
               {
                   expr += a[counter + j];
               }

               subProblemModel.add(expr == 1);

               counter += assSize[i];
           }

           counter = 0;
           for(i = 0; i < assNum; i++)
           {
               for(j = 0; j < assSize[i]; j++)
               {
                   for(k = 0; k < assSize[i]; k++)
                   {
                       if(j != k)
                       {
                           IloInt opt1 = optCode[counter + j];
                           IloInt opt2 = optCode[counter + k];

                           subProblemModel.add(a[counter + j] <= z[opt1][opt2]);
                       }
                   }
               }

               counter += assSize[i];
           }

           //Solve subproblem
           subProblemSolver.setParam(IloCplex::MIPDisplay, 1);
           subProblemSolver.solve();

           ///CHECK FOR STOP

           if(subProblemSolver.getObjValue() > -0.0001)
           {
               stop = true;
           }else
           {
               /// Add ranking data to list of columns
               cout << "***********************************************************" << endl;
               //cout << "New column: " << endl;
               IloIntArray newColumn(env, optProb.getSize());
               for(i = 0; i < newColumn.getSize(); i++)
               {
                   newColumn[i] = subProblemSolver.getValue(a[i]);
                   //cout << newColumn[i] << " ";
               }
               cout << endl;

               A.add(newColumn);

               IloIntArray newRankData(env, optNum);
               IloIntArray optPosition(env, optNum);

               for(i = 0; i < optNum; i++)
               {
                   newRankData[i] = i;
                   optPosition[i] = i;
               }

               for(i = 0; i < optNum-1; i++)
               {
                   for(j = i+1; j < optNum; j++)
                   {
                       if(subProblemSolver.getValue(z[newRankData[i]][newRankData[j]]) == 0)
                       {
                           IloInt tempValue = newRankData[i];
                           newRankData[i] = newRankData[j];
                           newRankData[j] = tempValue;
                       }
                   }
               }

//               cout << "Ranking data: ";
//               for(i = 0; i < optNum; i++)
//               {
//                   cout << newRankData[i] << " ";
//               }cout << endl;

               rankDataLst.add(newRankData);
               cout << "***********************************************************" << endl;
           }

           /// FREE MEMORY
           //Subproblem
           a.end();
           for(i = 0; i < optNum; i++)
           {
               z[i].end();
           }
           z.end();

           subProblemModel.end();

           subProblemSolver.end();

           price.end();

           //Restricted master problem
           pE.end();
           nE.end();
           lamda.end();
           resMasterModel.end();
           resMasterSolver.end();
       }
//      cout << "***********************************************************" << endl;
       cout << "Ranking data list: " << endl;
       for(i = 0; i < rankDataLst.getSize(); i++)
       {
           cout << "Ranking collect: ";
           for(j = 0; j < rankDataLst[i].getSize(); j++)
           {
               cout << rankDataLst[i][j] << " ";
           }cout << endl;
       }

   }
   catch(IloException& e) {
      cerr  << " ERROR: " << e << endl;   
   }
   catch(...) {
      cerr  << " ERROR" << endl;   
   }
   env.end();
   return 0;
}