#ifndef GUROBI_SOLVE_HPP
#define GUROBI_SOLVE_HPP

#include "gurobi_common.hpp"
#include "pds.hpp"

#include <boost/optional.hpp>

namespace pds {

MIPModel brimkovModel(Pds &input, bool inProp, bool outProp);

MIPModel jovanovicModel(Pds &inputs, bool inProp = true, bool outProp = true);

SolveResult solveMIP(const Pds &input, MIPModel &model,
                     boost::optional<std::string> output, std::ostream &solFile,
                     double timeLimit);

} // namespace pds

#endif // GUROBI_SOLVE_HPP
